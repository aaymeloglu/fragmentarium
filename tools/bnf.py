#!/usr/bin/env python3
"""Fetch pages of a Bibliothèque nationale de France manuscript, for comparison with a fragment.

    python3 tools/bnf.py 'Latin 15972' info                      # pages, labels, sizes
    python3 tools/bnf.py 'Latin 15972' overview OUTDIR --canvas 12
    python3 tools/bnf.py 'Latin 15972' tiles OUTDIR --canvas 12 [--cols 2] [--rows 4]
    python3 tools/bnf.py 'Latin 15972' crop OUTDIR x,y,w,h --canvas 12
    python3 tools/bnf.py btv1b9068482p info                      # by Gallica identifier

The commands are those of `tools/iiif.py`; the fetching ones need --canvas, since a book has
hundreds of pages. Canvas numbers are positions in the digitisation, from 0, not folio numbers:
`info` gives the library's label for each, which for a filmed manuscript is often "NP" (unnumbered)
on every opening, so find the folio by looking at overviews.

gallica.bnf.fr answers scripts with 403 and browsers with a robot check, so nothing here goes
there. Images and manifests come from BnF's API host (openapi.bnf.fr, IIIF 3, no upscaling). A
shelfmark is turned into a Gallica identifier through the manuscripts catalogue
(archivesetmanuscrits.bnf.fr), and the manifest's own label must then name that shelfmark, or the
tool stops. A shelfmark with no digitisation, or with several, is reported and not guessed at.
Searching the text of Gallica's printed books is not possible from a script.
Standard library only.
"""
import html
import json
import re
import sys
import urllib.parse
import urllib.request

import iiif

SEARCH = "https://archivesetmanuscrits.bnf.fr/resultatRechercheSimple.html?TEXTE_LIBRE_INPUT="
MANIFEST = "https://openapi.bnf.fr/iiif/presentation/v3/ark:/12148/{}/manifest.json"
DIGITISED = re.compile(r'val=https://gallica\.bnf\.fr/ark:/12148/(\w+)&amp;filtre=Dao"[^>]*>(.*?)\(\d+\)\s*</a>', re.S)


def _plain(text):
    return " ".join(html.unescape(text).replace("\xa0", " ").split()).casefold()


def digitised(page):
    """(Gallica identifier, shelfmark) for each digitised manuscript a catalogue result page lists."""
    return [(ark, " ".join(html.unescape(label).replace("\xa0", " ").split())) for ark, label in DIGITISED.findall(page)]


def identifiers(shelfmark, page):
    """Gallica identifiers the result page gives for exactly this shelfmark."""
    return [ark for ark, label in digitised(page) if _plain(label) == _plain(shelfmark)]


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=iiif.UA), timeout=60).read()


def label_of(manifest):
    return " ".join(text for texts in manifest.get("label", {}).values() for text in texts)


def canvases_of(manifest):
    """Canvases of an IIIF 3 manifest in the form `iiif.run` takes."""
    out = []
    for canvas in manifest["items"]:
        body = canvas["items"][0]["items"][0]["body"]
        base = body["service"][0]["id"] if body.get("service") else body["id"].split("/full/")[0]
        label = " ".join(text for texts in canvas.get("label", {}).values() for text in texts)
        out.append({"label": label, "base": base, "ext": "default.jpg", "w": canvas.get("width"),
                    "h": canvas.get("height"), "max_scale": 1.0, "note": None})
    return out


def resolve(name, fetch=get):
    """(Gallica identifier, manifest) for a shelfmark or an identifier; exits with the reason if there is not exactly one."""
    if re.fullmatch(r"btv1b\w+", name):
        return name, json.loads(fetch(MANIFEST.format(name)))
    page = fetch(SEARCH + urllib.parse.quote_plus(f'"{name}"')).decode("utf-8", "replace")
    found = identifiers(name, page)
    if len(found) != 1:
        listed = "; ".join(f"{label} = {ark}" for ark, label in digitised(page)) or "none"
        sys.exit(f"{len(found)} digitisations found for {name!r} in the BnF manuscripts catalogue. Listed there: {listed}")
    manifest = json.loads(fetch(MANIFEST.format(found[0])))
    if not _plain(label_of(manifest)).endswith(_plain(name)):
        sys.exit(f"{found[0]} is labelled {label_of(manifest)!r}, not {name!r}")
    return found[0], manifest


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    name, cmd = argv[0], argv[1]
    opts = {k.lstrip("-"): v for k, v in zip(argv[2:], argv[3:]) if k.startswith("--")}
    args = [a for a in argv[2:] if not a.startswith("--") and a not in opts.values()]
    if cmd != "info" and "canvas" not in opts:
        sys.exit("give --canvas N (see `info`): a book has too many pages to fetch all of them")
    ark, manifest = resolve(name)
    if cmd == "info":
        print(label_of(manifest), ark)
    iiif.run("bnf-" + ark, canvases_of(manifest), cmd, argv, opts, args)


if __name__ == "__main__":
    main(sys.argv[1:])
