#!/usr/bin/env python3
"""Search Schneyer's sermon repertory, volume by volume, in archive.org's full text.

    python3 tools/schneyer.py '"Videns Jesus civitatem"' '"templum Luc Videamus"~6'

J. B. Schneyer, Repertorium der lateinischen Sermones des Mittelalters (1150-1350), vols. 1-9,
lists sermons by author or manuscript with theme, incipit and explicit. The scans are on
archive.org with OCR. A full-text search across all of archive.org returns one hit per book with
a few highlights, which hides most entries; asking each volume separately shows them.

Queries use archive.org's full-text syntax: a quoted phrase, or a proximity search
`"word word word"~N` (the words within N words of each other, any order), which copes with
Schneyer's layout: theme, Bible reference in brackets, a dash, then the incipit. Useful pattern:
a theme word, "Luc"/"Matth"/"Joh", and one distinctive incipit word, ~6 to ~12.

Limits: OCR text; Schneyer normalises spelling (Jesus, quae, -ti-); the index volumes 10-11 are
not online; some archive.org items are mislabelled (0007-0009 are the anonymous volumes). A hit
is an incipit in a repertory: a lead. Find an edition or digitised manuscript and compare the
body of the sermon before claiming an identification.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

VOLUMES = ["repertoriumderla0001schn", "repertoriumderla0002unse", "repertoriumderla0003unse",
           "repertoriumderla0004schn", "repertoriumderla0005schn", "repertoriumderla0006schn",
           "repertoriumderla0007schn", "repertoriumderla0008schn", "repertoriumderla0009schn"]
API = "https://be-api.us.archive.org/fts/v1/search"


def url(query, volume):
    return API + "?q=" + urllib.parse.quote(f"{query} AND identifier:{volume}") + "&size=1"


def highlights(response):
    """Highlighted passages from one response, whitespace collapsed."""
    return [re.sub(r"\s+", " ", x).strip()
            for hit in response.get("hits", {}).get("hits", [])
            for x in hit.get("highlight", {}).get("text", [])]


def ask(query, volume):
    """One volume's response, or None after three failed tries."""
    for _ in range(3):
        try:
            req = urllib.request.Request(url(query, volume), headers={"User-Agent": "Mozilla/5.0"})
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception:
            time.sleep(5)
    return None


def main(argv):
    if not argv:
        sys.exit(__doc__)
    for query in argv:
        print("##", query, flush=True)
        # Each call takes ten seconds or more at archive.org; three at a time keeps a query under a
        # minute without crowding the service. Results print in volume order.
        with ThreadPoolExecutor(max_workers=3) as pool:
            responses = list(pool.map(lambda volume: ask(query, volume), VOLUMES))
        for volume, response in zip(VOLUMES, responses):
            if response is None:
                print("  ", volume[-8:], "| no response")
                continue
            for text in highlights(response):
                print("  ", volume[-8:], "|", text[:300], flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
