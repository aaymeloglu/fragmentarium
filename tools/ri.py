#!/usr/bin/env python3
"""Search the Regesta Imperii regests offline, from the project's open-data export.

    uv run python tools/ri.py fetch RI_13alles          # Friedrich III, with Chmel's regests and Anhang texts
    uv run python tools/ri.py search 'Tirol Landschaft' --from 1446-01-01 --to 1446-12-31
    uv run python tools/ri.py search 'Stams' --part RI_alles --limit 50

The Regesta Imperii publish their regest database under CC BY 4.0 as tab-separated files (named
.csv) in the repository gitlab.rlp.net/adwmainz/regesta-imperii/lab/regesta-imperii-data. The export
is not always current; the website is the latest text. regesta-imperii.de itself refuses scripted
requests, so search here and open a hit's permalink (printed with each hit) in a browser.

`fetch` downloads one part into ~/.cache/fragmentarium/ri (or $FRAGMENTARIUM_RI_DIR); `RI_alles`
is every part. `search` needs every word (case-insensitive, any order) somewhere in the regest's
place, summary, commentary, incipit, archival history or footnotes, optionally within a date range,
and prints identifier, date, place, the start of the summary and the permalink. Pass a part that
is not yet fetched and it is fetched first. Standard library only.
"""
import argparse
import csv
import os
import re
import sys
import urllib.request
from pathlib import Path

RAW = "https://gitlab.rlp.net/adwmainz/regesta-imperii/lab/regesta-imperii-data/-/raw/main/data/regesta-csv/{}.csv"
PERMALINK = "https://www.regesta-imperii.de/id/{}"
FIELDS = ("locality_string", "summary", "commentary", "incipit", "archival_history", "footnotes")


def cache_dir():
    return Path(os.environ.get("FRAGMENTARIUM_RI_DIR") or Path.home() / ".cache" / "fragmentarium" / "ri")


def fetch(part):
    path = cache_dir() / f"{part}.csv"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".part")
        with urllib.request.urlopen(RAW.format(part), timeout=600) as r, open(tmp, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        tmp.rename(path)
    return path


def plain(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def search(rows, words, start=None, end=None):
    words = [w.lower() for w in words]
    for row in rows:
        if start and (row.get("end_date") or "9999") < start:
            continue
        if end and (row.get("start_date") or "0000") > end:
            continue
        text = " ".join(plain(row.get(k)) for k in FIELDS).lower()
        if all(w in text for w in words):
            yield row


def read(path):
    csv.field_size_limit(sys.maxsize)
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("part", nargs="?", default="RI_alles")
    s = sub.add_parser("search")
    s.add_argument("words")
    s.add_argument("--part", default="RI_13alles")
    s.add_argument("--from", dest="start")
    s.add_argument("--to", dest="end")
    s.add_argument("--limit", type=int, default=30)
    a = ap.parse_args()
    if a.cmd == "fetch":
        print(fetch(a.part))
        return
    n = 0
    for row in search(read(fetch(a.part)), a.words.split(), a.start, a.end):
        n += 1
        if n <= a.limit:
            print(f"{row['identifier']} | {row.get('date_string') or row.get('start_date')} | {row.get('locality_string')}")
            print("   ", plain(row.get("summary"))[:300])
            print("   ", PERMALINK.format(row["persistent_identifier"]))
    print(f"{n} hits" + (f", first {a.limit} shown" if n > a.limit else ""))


if __name__ == "__main__":
    main()
