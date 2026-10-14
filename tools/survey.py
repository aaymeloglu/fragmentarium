#!/usr/bin/env python3
"""Survey candidate records before choosing a batch: image sizes, catalogue knowledge, contact sheets.

    uv run python tools/survey.py --cache /tmp/survey                 # every record not yet in the ledger
    uv run python tools/survey.py --cache /tmp/survey F-xxxx F-yyyy   # these records
    uv run --group images python tools/survey.py --cache /tmp/survey --sheets /tmp/survey/sheets

For each record it prints the catalogue's size in millimetres, the number of images, the native
pixel size of the first images, the pixels per millimetre those imply at best, whether the record
page links a full description, and the catalogue title. Records are listed with the most pixels
per millimetre first (those without a catalogue size last), and flagged:

    SMALL  no image is wider or taller than --small pixels (default 1200): whatever the leaf, it
           cannot be read at that size
    DESC   the record page links a full description: read it (`tools/catalogue.py`) before
           treating the record as unidentified
    ERR    the manifest or an image size could not be fetched
    SIB    a ledger record of the same library shares a shelfmark with this one (a reconstruction
           record lists the shelfmarks of its parts); the last column names it and its status.
           Look at that record before choosing: the two may be one leaf, or one already examined

The pixel figures describe the photograph, not the fragment: a strip on a large background, or a
fragment still inside a binding, has far fewer pixels across its text than the image has. The
contact sheets (--sheets, needs Pillow) show the first images of each record side by side for
that judgement; they are for choosing, never for transcribing.

Manifests, sizes and record pages are kept in --cache, so a second run costs nothing. Without ids
the candidates are the rows of the latest catalogue sweep (`sweep.py`) that have no ledger row.
"""
import argparse
import csv
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import catalogue
import iiif

ROOT = Path(__file__).resolve().parents[1]
SWEEP = max((ROOT / "data").glob("unidentified-*.csv"))  # the latest sweep.py list
LEDGER = ROOT / "data" / "fragments.json"


def candidates(sweep=SWEEP, ledger=LEDGER):
    """Sweep rows about an unidentified text (scope `title`; every row of a list without scopes) and
    with no ledger row, as {id: row}."""
    done = {row["id"] for row in json.loads(Path(ledger).read_text(encoding="utf-8"))}
    with open(sweep, newline="", encoding="utf-8") as handle:
        return {row["fragmentarium_id"]: row for row in csv.DictReader(handle)
                if row["fragmentarium_id"] not in done and row.get("scope", "title") == "title"}


def siblings(shelfmark, ledger):
    """Ledger rows of the same library that share a shelfmark with a sweep row, as "F-id (status)".

    The sweep gives "library, shelfmark"; the ledger keeps the two apart. A reconstruction record's
    shelfmark is the list of its parts' shelfmarks, so a row is a sibling when the two shelfmarks
    are the same or one is a whole item of the other's list. Shelfmarks that merely begin alike
    ("Album II, nr. 3" and "Album II, nr. 8") are not siblings.
    """
    out = []
    for row in ledger:
        library, theirs = row.get("institution"), row.get("shelfmark")
        if not (library and theirs and (shelfmark or "").startswith(library + ", ")):
            continue
        ours = shelfmark[len(library) + 2:]
        if f", {ours}, " in f", {theirs}, " or f", {theirs}, " in f", {ours}, ":
            out.append(f"{row['id']} ({row.get('status', '?')})")
    return out


def millimetres(text):
    """The largest two numbers in a catalogue dimension string, long side first; None if there are not two."""
    numbers = sorted((float(n.replace(",", ".")) for n in re.findall(r"\d+(?:[.,]\d+)?", text or "")), reverse=True)
    return (numbers[0], numbers[1]) if len(numbers) >= 2 else None


def density(sizes, mm):
    """Upper bound on pixels per millimetre: the largest image's long side over the fragment's long side."""
    longest = max((max(w, h) for w, h in sizes if w and h), default=0)
    return round(longest / mm[0], 1) if longest and mm and mm[0] else None


def flags(sizes, has_description, error, small=1200, sibling=False):
    out = []
    if error:
        out.append("ERR")
    elif not sizes or max(max(w or 0, h or 0) for w, h in sizes) < small:
        out.append("SMALL")
    if has_description:
        out.append("DESC")
    if sibling:
        out.append("SIB")
    return out


def cached(path, url):
    if path.exists():
        return path.read_bytes()
    data = urllib.request.urlopen(urllib.request.Request(url, headers=iiif.UA), timeout=60).read()
    path.write_bytes(data)
    time.sleep(0.5)
    return data


def look(fid, cache, images=4):
    """One record: manifest, first image sizes and description links, all through the cache."""
    folder = cache / fid
    folder.mkdir(parents=True, exist_ok=True)
    out = {"id": fid, "sizes": [], "canvases": [], "images": 0, "description": False, "error": None, "mm": "", "title": ""}
    try:
        manifest = json.loads(cached(folder / "manifest.json", f"{catalogue.SITE}/metadata/iiif/{fid}/manifest.json"))
        for item in manifest.get("metadata", []):
            if str(item.get("label", "")).startswith("Current Dimensions"):
                out["mm"] = catalogue.plain(str(item.get("value")))
            if item.get("label") == "Title":
                out["title"] = catalogue.plain(str(item.get("value")))

        def probe(base):
            info = json.loads(cached(folder / ("info-" + re.sub(r"\W+", "_", base)[-80:] + ".json"), base + "/info.json"))
            return info["width"], info["height"]

        canvases = iiif.canvases_of(manifest, probe=probe)
        out["images"] = len(canvases)
        out["canvases"] = canvases[:images]
        out["sizes"] = [(c["w"], c["h"]) for c in canvases[:images]]
    except Exception as error:
        out["error"] = str(error)[:80]
        return out
    try:
        page = cached(folder / "overview.html", f"{catalogue.SITE}/overview/{fid}").decode("utf-8", "replace")
        out["description"] = bool(catalogue.description_links(fid, page))
    except Exception as error:
        out["error"] = "record page: " + str(error)[:60]
    return out


def sheets(records, cache, outdir, per_sheet=5, width=440):
    """Contact sheets: one row per record, its first images reduced, the id above the row."""
    from PIL import Image, ImageDraw

    outdir.mkdir(parents=True, exist_ok=True)
    row_height = width + 22
    for start in range(0, len(records), per_sheet):
        chunk = records[start:start + per_sheet]
        columns = max(1, max(len(r["canvases"]) for r in chunk))
        sheet = Image.new("RGB", (width * columns, row_height * len(chunk)), "white")
        draw = ImageDraw.Draw(sheet)
        for row, rec in enumerate(chunk):
            draw.text((4, row * row_height + 4), f"{rec['id']}  {' '.join(rec['flags'])}", fill="red")
            for column, canvas in enumerate(rec["canvases"]):
                if (canvas.get("note") or "").startswith("FAULT"):
                    continue
                path = cache / rec["id"] / f"thumb-{column}.jpg"
                try:
                    cached(path, f"{canvas['base']}/full/!900,900/0/{canvas['ext']}")
                    image = Image.open(path).convert("RGB")
                    image.thumbnail((width - 4, width))
                    sheet.paste(image, (column * width, row * row_height + 20))
                except Exception as error:
                    draw.text((column * width + 4, row * row_height + 24), f"image {column}: {str(error)[:40]}", fill="black")
        name = outdir / f"sheet-{start // per_sheet:02d}.jpg"
        sheet.save(name, quality=85)
        print(name, " ".join(r["id"] for r in chunk), file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ids", nargs="*")
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--sheets", type=Path, help="directory for contact sheets (needs Pillow)")
    parser.add_argument("--small", type=int, default=1200)
    parser.add_argument("--images", type=int, default=4, help="images per record to size and show")
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    rows = candidates()
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    ids = args.ids or list(rows)
    records = []
    for fid in ids:
        rec = look(fid, args.cache, args.images)
        row = rows.get(fid, {})
        rec["mm"] = rec["mm"] or row.get("dimensions_mm", "")
        rec["title"] = rec["title"] or row.get("title", "")
        rec["density"] = density(rec["sizes"], millimetres(rec["mm"]))
        rec["siblings"] = siblings(row.get("shelfmark", ""), ledger)
        rec["flags"] = flags(rec["sizes"], rec["description"], rec["error"], args.small, bool(rec["siblings"]))
        records.append(rec)
        print(fid, " ".join(rec["flags"]), file=sys.stderr, flush=True)
    records.sort(key=lambda r: (r["density"] is None, -(r["density"] or 0)))
    print("id\tflags\tmm\timages\tpixels\tpx/mm at most\ttitle\tledger siblings")
    for rec in records:
        pixels = " ".join(f"{w}x{h}" for w, h in rec["sizes"]) or (rec["error"] or "")
        print("\t".join([rec["id"], ",".join(rec["flags"]), rec["mm"], str(rec["images"]), pixels,
                         str(rec["density"] or ""), rec["title"][:70], " ".join(rec["siblings"])]))
    if args.sheets:
        sheets(records, args.cache, args.sheets)


if __name__ == "__main__":
    main()
