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
Not every unidentified text is catalogued with one of those words: many records are titled only by
kind, "Legal text", "Sermones", "Commentary on the Psalms", "Latin fragment". The sweep therefore also
walks the whole catalogue (the empty search, one country at a time because a search returns at most
3,000 results) and keeps a record whose title names no author or work, only a kind of text: scope
`generic` (`generic()` decides; see its docstring). Liturgical and biblical books are not generic:
"Missal" or "Antiphonal" says what the book was, and settling which feast a leaf holds is a
different search (`cantus.py`). `survey.py` takes `generic` rows as candidates with the `title` ones.
`--no-catalogue` skips the walk.

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
# Without an Accept header Fragmentarium answers 404 for some manifests that exist.
UA = {"User-Agent": "Mozilla/5.0 (fragmentarium tools)", "Accept": "*/*"}
TERMS = ["unidentified", "unknown", '"nicht identifiziert"', "unidentifiziert", '"non identificato"',
         '"non identificata"', '"non identifié"', '"non identifiée"', '"no identificado"',
         "ongeïdentificeerd", '"niet geïdentificeerd"', "oidentifierad", '"ej identifierad"']
TITLES = {"Title", "Subtitle", "Text title of the content item"}
RECORD_FIELDS = TITLES | {"Document summary"}
# Words a title may consist of and still name no particular text. A title made only of these (after
# languages, "fragment of", qualifiers like "(?)" and a parenthesised shelfmark are dropped) is generic.
KIND_WORDS = set("""
text texts textual treatise treatises tract tractatus fragment fragments fragmentum fragmenta leaf leaves strip strips
sermon sermons sermones sermo homily homilies homilia homiliae commentary commentaries commentarius gloss glosses glossed
legal law laws juridical canon canonical civil roman theological theology theologica theologicus medical medicinal medicine
scientific astronomical astrological mathematical philosophical philosophy logic logical scholastic exegetical exegesis
grammar grammatical glossary vocabulary florilegium excerpts extracts miscellany miscellaneous collection compilation
prayer prayers prayerbook book devotional spiritual religious meditation meditations moral moralia ascetic mystical
poem poems poetry verse verses hymn rhymed song songs narrative chronicle historical history hagiographical lives life vita
saint saints legend legends letter letters notes note quaestio quaestiones question questions disputed summa
unknown unidentified unidentifiable uncertain undetermined indeterminate anonymous work works writing piece pieces part
probatio pennae school exercise exercises tables table index manuscript manuscripts codex printed print incunable
on of the a an and or with in from to for about de et cum super in
""".split())
LANGUAGE_WORDS = set("""latin latina latinus greek hebrew arabic coptic syriac armenian ethiopic old middle dutch german
high low french anglo norman english italian spanish castilian catalan portuguese occitan provençal czech polish
hungarian icelandic norse swedish danish irish welsh church slavonic vernacular bilingual""".split())
# A title that names a kind of book as a whole: what the book was is known, so the title is not generic.
NAMED_BOOK = re.compile(r"antiphon|gradua|missal|missale|breviar|psalt|hours|horae|sacrament|sequen|hymn(al|ar)|lection|kyriale|"
                        r"calend|necrolog|obituar|processional|rituale|choirbook|evangel|gospel|pontific|ordinal|liturg|ordinarium|"
                        r"martyrolog|tropa?r|diurnal|homiliar|legendar|passional|charter|cartular|register|account|deed|urbar|"
                        r"\bbibl|testament|vulgat|qur|torah|polyphon|music|musik|noted|neume|choral|office|officium|rotul|"
                        r"\bdocument|letter of|indulgence|binding|cover|wrapper|diagram|inventory", re.I)
# "Commentary on the Psalms", "Treatise on logic": a kind of text on a subject, with no author or title of its own.
ON_SUBJECT = re.compile(r"^(?:\w+ ){0,2}(?:commentary|commentaries|gloss|glosses|lectura|treatise|tract|sermons?|questions?|quaestiones|"
                        r"notes|summa|excerpts?|extracts?|treatment)\b(?: \w+){0,2} (?:on|to|of|in|super|de)\b", re.I)


def generic(title):
    """True when a catalogue title names only a kind of text, not an author or a work.

    "Legal text", "Theological Texts (Fragm. lat. VII 31)", "Sermones de tempore", "Middle Dutch
    prayer book (?)": every word is a kind, a language or a connective. "Commentary on the Psalms",
    "Question commentary on Aristoteles' Physica": a kind of text on a subject, with no author
    before it. Not generic: an author or work ("Petrus Lombardus, Sententiae", "Bede's commentary
    on Luke"), or a book named by type ("Missal", "Glossed Bible", "Book of Hours"), whose leaf is
    a liturgical or biblical search, not this one. An empty title is generic."""
    t = re.sub(r"\([^)]*\d[^)]*\)", " ", title)                  # parenthesised shelfmark
    t = re.sub(r"[?()\[\]]", " ", t).strip(" .,;:-")
    if not t:
        return True
    if NAMED_BOOK.search(t) or re.search(r"\bby [A-Z]", t):
        return False
    if ON_SUBJECT.match(t) and "'s " not in t and "," not in t.split(" on ")[0]:
        return True
    words = re.findall(r"[^\W\d_]+", t.lower())
    return bool(words) and all(w in KIND_WORDS or w in LANGUAGE_WORDS for w in words)


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


def countries(page):
    """The country facet values offered on a search page."""
    return sorted(set(re.findall(r'name="aSelectedFacets\[country_code_facet\]\[\]"\s+value="([^"]+)"', page)))


def browse(country, page, per_page=500):
    query = urllib.parse.urlencode({"sQueryString": "", "iResultsPerPage": per_page, "iCurrentPage": page,
                                    "aSelectedFacets[country_code_facet][]": country})
    with urllib.request.urlopen(urllib.request.Request(f"{SEARCH}?{query}", headers=UA), timeout=120) as response:
        return response.read().decode("utf-8", "replace")


def walk(get=browse, first=lambda: fetch("", 1, per_page=10), pause=1.0, per_page=500):
    """Every record of the catalogue, {id: result row}, one country facet at a time (a search lists
    at most 3,000 results; the largest country holds fewer)."""
    rows = {}
    for country in countries(first()):
        page = 1
        while True:
            found = list(results(get(country, page)))
            for hit in found:
                rows.setdefault(hit["fragmentarium_id"], hit)
            if len(found) < per_page:
                break
            page += 1
            time.sleep(pause)
    return rows


def add_generic(rows, catalogue_rows):
    """Records of the whole catalogue with a generic title that the term search did not find as
    `title`, added (or re-scoped from `description`/`host`) with scope `generic`. Returns how many."""
    added = 0
    for fid, hit in catalogue_rows.items():
        if not generic(hit["title"]) or rows.get(fid, {}).get("scope") == "title":
            continue
        row = rows.setdefault(fid, {**hit, "found_in": [], "terms": []})
        row["scope"] = "generic"
        row["terms"] = row["terms"] + ["(generic title)"]
        added += 1
    return added


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
    parser.add_argument("--no-catalogue", action="store_true", help="skip the whole-catalogue walk for generic titles")
    args = parser.parse_args()
    rows = sweep(args.term or TERMS)
    if not args.no_catalogue:
        everything = walk()
        print(f"catalogue: {len(everything)} records; {add_generic(rows, everything)} with a generic title")
    for fid, row in sorted(rows.items()):
        if row["scope"] in ("title", "generic"):
            try:
                enrich(row, manifest(fid))
            except Exception as error:  # a missing manifest leaves the search fields only
                row["notes"] = f"manifest not read: {error}"
            time.sleep(0.3)
    write(rows, args.out)
    counts = {s: sum(r["scope"] == s for r in rows.values()) for s in ("title", "generic", "description", "host")}
    print(f"{len(rows)} records to {args.out}: " + ", ".join(f"{s} {n}" for s, n in counts.items()))


if __name__ == "__main__":
    main()
