#!/usr/bin/env python3
"""Do the anchor phrases of a fragment sit together in one passage of an archive.org volume?

    python3 tools/ia_cluster.py IDENTIFIER "phrase one" "phrase two" ... [--window 6000] [--show]

Downloads the volume's OCR (cached in ~/.cache/fragmentarium/), matches each phrase with
whitespace and long-s tolerance ([sſf] for s, u/v and ae/e/oe interchangeable), and for every
occurrence of the first phrase reports how many of the others fall within --window characters.
A score equal to the number of phrases is a passage worth reading; scattered single hits across a
big volume are not. --show prints the best window. Standard library only.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

CACHE = Path.home() / ".cache" / "fragmentarium"
UA = {"User-Agent": "Mozilla/5.0 (fragmentarium tools)"}


def ocr_text(ident):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{ident}.txt"
    if p.exists() and p.stat().st_size > 1000:
        return p.read_text(errors="replace")
    files = json.load(urllib.request.urlopen(urllib.request.Request(f"https://archive.org/metadata/{ident}/files", headers=UA), timeout=60))["result"]
    names = [f["name"] for f in files if f["name"].endswith("_djvu.txt")]
    if not names:
        sys.exit(f"{ident}: no _djvu.txt (OCR missing or access-restricted)")
    url = f"https://archive.org/download/{ident}/{urllib.parse.quote(names[0])}"
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600).read()
    if len(data) < 1000 or b"<html" in data[:200].lower():
        sys.exit(f"{ident}: OCR download refused ({len(data)} bytes); volume may be lending-only")
    p.write_bytes(data)
    return data.decode("utf-8", "replace")


def pattern(phrase):
    out = []
    for ch in phrase.lower():
        if ch.isspace():
            out.append(r"\s+")
        elif ch == "s":
            out.append(r"[sſf]")
        elif ch in "uv":
            out.append("[uv]")
        elif ch in "ij":
            out.append("[ij]")
        elif ch == "e":
            out.append(r"(?:e|ae|oe|æ|œ)")
        else:
            out.append(re.escape(ch))
    return re.compile("".join(out), re.I)


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    window, show = 6000, False
    phrases = []
    it = iter(argv[1:])
    for a in it:
        if a == "--window":
            window = int(next(it))
        elif a == "--show":
            show = True
        else:
            phrases.append(a)
    t = ocr_text(argv[0])
    hits = {ph: [m.start() for m in pattern(ph).finditer(t)] for ph in phrases}
    for ph, h in hits.items():
        print(f"{len(h):4d}  {ph}")
    first = phrases[0]
    best = (0, None)
    for p0 in hits[first]:
        near = {ph: any(abs(x - p0) < window for x in hits[ph]) for ph in phrases[1:]}
        score = 1 + sum(near.values())
        if score > best[0]:
            best = (score, p0)
        if score >= 2:
            print(f"@{p0}: score {score}/{len(phrases)}  " + "  ".join(f"{'+' if v else '-'}{k[:18]}" for k, v in near.items()))
    if best[1] is not None and show:
        p0 = best[1]
        print("\n" + re.sub(r"\s+", " ", t[max(0, p0 - window // 2):p0 + window // 2]))
    print(f"\nbest score {best[0]}/{len(phrases)}")


if __name__ == "__main__":
    main(sys.argv[1:])
