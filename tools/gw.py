#!/usr/bin/env python3
"""List digitised copies of an incunable from its Gesamtkatalog der Wiegendrucke number.

    python3 tools/gw.py M32924          # Pharetra doctorum, Strasbourg: Mentelin
    python3 tools/gw.py 04282

Google Books snippets of fifteenth-century prints are enough to find a candidate but not to
verify one: the OCR is garbled and no page is shown. GW's "Reproduktionen" line names the
libraries with a page-readable scan (often Munich, whose identifier bsbNNNNNNNN also gives a
IIIF manifest at https://api.digitale-sammlungen.de/iiif/presentation/v2/<id>/manifest).
The GW number is printed in ISTC and in most library records. Check that the scan is the
edition you mean: different works share short titles. Standard library only.
"""
import html
import re
import sys
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (fragmentarium tools)"}


def parse(page):
    """Return (heading, [links]) from a GW incunable page."""
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(page))).strip()
    m = re.search(r"GW\. Incunable \S+ (.*)", text)
    heading = re.split(r" Reproduktionen| Vorlage:", m.group(1) if m else text)[0].strip()[:200]
    links = []
    for u in re.findall(r'href="(https?://[^"]+)"', page):
        if re.search(r"gesamtkatalogderwiegendrucke|gwshow|purl\.org|d-nb\.info", u):
            continue
        if u not in links:
            links.append(html.unescape(u))
    return heading, links


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        sys.exit(__doc__)
    number = args[0].upper()
    url = f"https://www.gesamtkatalogderwiegendrucke.de/docs/{'GW' if number[0].isdigit() else ''}{number}.htm"
    page = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read().decode("utf-8", "replace")
    heading, links = parse(page)
    print(heading)
    for u in links:
        print(" ", u)


if __name__ == "__main__":
    main()
