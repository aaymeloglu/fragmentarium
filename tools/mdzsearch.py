#!/usr/bin/env python3
"""Full-text search of the Munich Digitisation Centre's OCR (digitale-sammlungen.de).

    uv run python tools/mdzsearch.py '"de templorum dedicatione" encaenia' [--n 20]

MDZ holds page-level OCR for a very large share of sixteenth- to eighteenth-century printed
books in Bavarian libraries, including many that Google Books has scanned but does not return
in a phrase search. Each hit gives the volume id (bsbNNNNNNNN), title, author, date and OCR
snippets. Read the page itself before relying on it:

    https://www.digitale-sammlungen.de/en/view/<id>?page=<scan>
    https://api.digitale-sammlungen.de/iiif/image/v2/<id>_<scan as 5 digits>/full/1400,/0/default.jpg

A hit is a lead; early-print OCR is noisy, so try spelling variants and short phrases.
Standard library only, no key.
"""
import argparse
import json
import re
import urllib.parse
import urllib.request

API = "https://www.digitale-sammlungen.de/api/search"


def search(query, n=10):
    url = API + "?" + urllib.parse.urlencode(
        {"query": query, "handler": "simple-fulltext", "ocrContext": 1, "pageSize": n})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--json", action="store_true", help="print the raw response")
    a = ap.parse_args()
    data = search(a.query, a.n)
    if a.json:
        print(json.dumps(data, indent=1, ensure_ascii=False))
        return
    print("total", data.get("numTotal"))
    for doc in data.get("docs", []):
        snippets = [re.sub(r"<[^>]+>", "", s.get("text", "")).replace("\n", " ")[:240]
                    for s in (doc.get("ocrSnippets") or [])[:3]]
        print(doc.get("id") or doc.get("volumeId"), "|", str(doc.get("title"))[:100], "|",
              doc.get("authors") or doc.get("persInst") or "", "|",
              doc.get("date") or doc.get("datePublished") or "")
        for s in snippets:
            print("   ", s)


if __name__ == "__main__":
    main()
