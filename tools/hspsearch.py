#!/usr/bin/env python3
"""Search Handschriftenportal, the German manuscript portal, and list digital copies.

    python3 tools/hspsearch.py '"De regiminibus tractantes"' 'Ungarus Sermones' [--raw]

The portal holds the full text of many printed and online catalogue descriptions of manuscripts
in German collections, so a quoted incipit, a work title or a shelfmark can find other witnesses
of an unprinted text. For each hit this prints place, library, shelfmark, date, any digital copy
(IIIF manifest or viewer link) and the catalogue passages that matched.

A hit is a catalogue description. Open the digital copy and read the text before relying on it;
catalogues give different texts the same author and title. No hit does not mean no manuscript:
coverage is partial and many descriptions give titles without incipits.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://handschriftenportal.de/api/hspobjects/search"


def url(query, rows=10):
    return API + "?" + urllib.parse.urlencode({"q": query, "start": 0, "rows": rows, "sort": "score-desc",
                                               "fq": "{}", "hl": "true", "isExtended": "false"})


def rows(response):
    """(place, library, shelfmark, date, [digital links], [matched passages]) per manuscript."""
    highlighting = response.get("highlighting") or response.get("metadata", {}).get("highlighting") or {}
    out = []
    for p in response.get("payload", []):
        o = p.get("hspObject", {})
        digital = [x.get("manifest-url-display") or x.get("external-url-display")
                   for x in p.get("hspDigitizeds", [])]
        passages = []
        for key in [o.get("id")] + [x.get("id") for x in p.get("hspDescriptions", [])]:
            for found in highlighting.get(key, {}).values():
                passages += [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip() for s in found[:2]]
        out.append((o.get("settlement-display"), o.get("repository-display"), o.get("idno-display"),
                    o.get("orig-date-lang-display"), [d for d in digital if d], passages))
    return out


def main(argv):
    raw = "--raw" in argv
    queries = [a for a in argv if a != "--raw"]
    if not queries:
        sys.exit(__doc__)
    for query in queries:
        try:
            req = urllib.request.Request(url(query), headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            response = json.load(urllib.request.urlopen(req, timeout=90))
        except Exception as error:
            print("##", query, "ERR", error)
            continue
        if raw:
            print(json.dumps(response, ensure_ascii=False)[:6000])
            continue
        meta = response.get("metadata", {})
        print("##", query, "->", meta.get("numGroupsFound", meta.get("numFound")))
        for place, library, shelfmark, date, digital, passages in rows(response):
            print("  ", place, "|", library, "|", shelfmark, "|", date, "| digital:", ", ".join(digital[:2]) or "none listed")
            for passage in passages:
                print("       ", passage[:330])
        time.sleep(0.5)


if __name__ == "__main__":
    main(sys.argv[1:])
