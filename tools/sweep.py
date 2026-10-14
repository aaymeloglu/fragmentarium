#!/usr/bin/env python3
"""Sweep Fragmentarium's search for records whose own text is catalogued as unidentified.

    uv run python tools/sweep.py                          # writes data/unidentified-<today>.csv
    uv run python tools/sweep.py --out /tmp/sweep.csv --term 'oidentifierad'

Each term goes to the site's full-text search (all metadata fields, stemmed, so "unidentified"
also finds "unidentifiable" and "not identified"), and every page of results is read. A result
says which fields matched. A record whose title, subtitle or text title matched is about an
unidentified text, and so is one whose document summary matched (it says what the record holds,
and is where most catalogues name an unidentified part): scope `title`. A match only in the
description of a content item, the host volume or the provenance ("many fragments of this collection are still unidentified") is scope
`description` or `host`; those rows are kept for reference (`host` also takes "unknown" outside a title), and `survey.py` takes only `title`
rows as candidates. Terms in other languages catch records catalogued in them; "unknown" counts
only when the title itself matched, since it mostly matches unknown provenance.

The CSV is the corpus list: one row per record, with the terms and fields that matched, the
headline (material, extent, date, size), the date it went online, and the first matching snippet;
`title` rows also get the manifest's century, language, script, extent, size, area, number of
images and the start of its reconstruction summary, which `docs/_build_site.py` ranks the
burndown page by.
Run it again to refresh the list; compare with the previous file to see what is new. Standard
library only.
"""
import argparse
import csv
import datetime
import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import catalogue
import survey

ROOT = Path(__file__).resolve().parents[1]
SEARCH = "https://fragmentarium.ms/search"
UA = {"User-Agent": "Mozilla/5.0 (fragmentarium tools)"}
TERMS = ["unidentified", "unknown", '"nicht identifiziert"', "unidentifiziert", '"non identificato"',
         '"non identificata"', '"non identifié"', '"non identifiée"', '"no identificado"',
         "ongeïdentificeerd", '"niet geïdentificeerd"', "oidentifierad", '"ej identifierad"']
TITLES = {"Title", "Subtitle", "Text title of the content item"}
RECORD_FIELDS = TITLES | {"Document summary"}
COLUMNS = ["fragmentarium_id", "url", "shelfmark", "century", "language", "script", "items", "dimensions_mm",
           "area_mm2", "images", "title", "notes", "headline", "online_since", "scope", "found_in", "terms", "snippet"]
FIELDS = {"Century": "century", "Text Language": "language", "Script Type": "script",
          "Number of Fragment Items": "items", "Current Dimensions (in mm)": "dimensions_mm"}


def text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def fetch(term, page, per_page=100):
    query = urllib.parse.urlencode({"sQueryString": term, "iResultsPerPage": per_page, "iCurrentPage": page})
    with urllib.request.urlopen(urllib.request.Request(f"{SEARCH}?{query}", headers=UA), timeout=120) as response:
        return response.read().decode("utf-8", "replace")


def results(page):
    """One dict per result block of a search page."""
    for block in page.split('<div class="search-result row">')[1:]:
        titles = [text(t) for t in re.findall(r'<div class="document-title">(.*?)</div>', block, re.S)]
        fid = next((t for t in titles if re.fullmatch(r"F-[a-z0-9]{4}", t)), None)
        if not fid:
            continue
        headline = re.search(r'<div class="document-headline">(.*?)</div>', block, re.S)
        shelfmark = re.search(r'<p class="serif[^"]*">(.*?)</p>', block, re.S)
        since = re.search(r"Online Since: ([\d/]+)", block)
        found = [text(f) for f in re.findall(r'<span class="found-in">Found in: (.*?)</span>', block, re.S)]
        snippets = [text(s) for s in re.findall(r'<span class="search-result-snippet">(.*?)</span>', block, re.S)]
        head = text(headline.group(1)) if headline else ""
        yield {"fragmentarium_id": fid, "url": f"https://fragmentarium.ms/overview/{fid}",
               "shelfmark": text(shelfmark.group(1)) if shelfmark else "",
               "title": titles[0] if titles and titles[0] != fid else "", "headline": head,
               "dimensions_mm": head.split("·")[-1].strip() if "mm" in head.split("·")[-1] else "",
               "online_since": since.group(1) if since else "", "found_in": found,
               "snippet": snippets[0] if snippets else ""}


def scope(fields):
    if RECORD_FIELDS & set(fields):
        return "title"
    if any("host volume" in field for field in fields):
        return "host" if all("host volume" in field for field in fields) else "description"
    return "description"


def sweep(terms, get=fetch, pause=1.0):
    """{id: row} over all terms; fields and terms that matched are merged across terms."""
    rows = {}
    for term in terms:
        page = 1
        while True:
            found = list(results(get(term, page)))
            for hit in found:
                row = rows.setdefault(hit["fragmentarium_id"], {**hit, "found_in": [], "terms": []})
                row["found_in"] += [f for f in hit["found_in"] if f not in row["found_in"]]
                row["terms"].append(term.strip('"'))
            if not found:
                break
            page += 1
            time.sleep(pause)
    for row in rows.values():
        row["scope"] = scope(row["found_in"])
        if row["terms"] == ["unknown"] and not TITLES & set(row["found_in"]):
            row["scope"] = "host"  # "unknown" outside a title is mostly provenance, not the text
    return rows


def manifest(fid):
    url = f"https://fragmentarium.ms/metadata/iiif/{fid}/manifest.json"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as response:
        return json.load(response)


def enrich(row, record):
    """Catalogue fields of a manifest added to a sweep row: century, language, script, extent, size,
    area, number of images and the start of the reconstruction summary."""
    meta = {item.get("label"): item.get("value") for item in record.get("metadata", [])}
    for label, key in FIELDS.items():
        if meta.get(label):
            row[key] = catalogue.plain(str(meta[label])).replace("\n", "; ")
    mm = survey.millimetres(row.get("dimensions_mm"))
    row["area_mm2"] = round(mm[0] * mm[1]) if mm else ""
    row["images"] = len(record.get("sequences", [{}])[0].get("canvases", []))
    row["notes"] = " ".join(catalogue.plain(str(meta.get("Reconstruction Summary") or "")).split())[:200]
    return row


def write(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        out = csv.DictWriter(handle, fieldnames=COLUMNS, extrasaction="ignore")
        out.writeheader()
        for fid in sorted(rows):
            row = rows[fid]
            out.writerow({**row, "found_in": "; ".join(row["found_in"]), "terms": "; ".join(row["terms"])})


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=ROOT / "data" / f"unidentified-{datetime.date.today()}.csv")
    parser.add_argument("--term", action="append", help="search these terms instead of the default list")
    args = parser.parse_args()
    rows = sweep(args.term or TERMS)
    for fid, row in sorted(rows.items()):
        if row["scope"] == "title":
            try:
                enrich(row, manifest(fid))
            except Exception as error:  # a missing manifest leaves the search fields only
                row["notes"] = f"manifest not read: {error}"
            time.sleep(0.3)
    write(rows, args.out)
    counts = {s: sum(r["scope"] == s for r in rows.values()) for s in ("title", "description", "host")}
    print(f"{len(rows)} records to {args.out}: " + ", ".join(f"{s} {n}" for s, n in counts.items()))


if __name__ == "__main__":
    main()
