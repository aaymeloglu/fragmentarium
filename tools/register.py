#!/usr/bin/env python3
"""Add unresearched fragments to data/fragments.json from their cached Fragmentarium manifests.

    uv run python tools/register.py F-xxxx F-yyyy ...

A fragment must have a ledger row before `readings.py freeze` will save a reading for it. This
writes that row from the manifest `acquire_batch.py` cached (institution, shelfmark, catalogue
title and date, dimensions, thumbnail), with status `unidentified`, confidence `none` and a
placeholder note to be replaced when the research is recorded. Existing rows are left alone.
Standard library only.
"""
import argparse
import datetime
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "fragments.json")
PLACEHOLDER = "First reading preserved; source research not yet recorded."
# Fragmentarium collection names that are placeholders, mapped to the holding archive.
COLLECTIONS = {"Stams (Stealth Published)": "Stiftsarchiv"}


def thumbnail(manifest, canvas=0):
    """240-pixel thumbnail address of one canvas. Canvas 0 is often the back of a sheet, so
    `record.py` can point the thumbnail at the text face with `thumbnail_canvas`."""
    image = manifest["sequences"][0]["canvases"][canvas]["images"][0]["resource"]
    service = image.get("service", {}).get("@id")
    if service:
        native = "native" if "gallica.bnf.fr" in service else "default"
        thumb = f"{service}/full/240,/0/{native}.jpg"
    else:
        thumb = image["@id"]
    return thumb.replace("http://", "https://")


def row(fid, cache, order, today):
    m = json.load(open(os.path.join(cache, fid, "manifest.json"), encoding="utf-8"))
    md = {x["label"]: re.sub(r"<[^>]+>", "", str(x["value"])).strip() for x in m.get("metadata", [])}
    title = md.get("Title", "")
    if md.get("Subtitle"):
        title += " | " + md["Subtitle"]
    record = f"https://fragmentarium.ms/overview/{fid}"
    return {
        "id": fid,
        "record": record,
        "manifest": f"https://fragmentarium.ms/metadata/iiif/{fid}/manifest.json",
        "thumbnail": thumbnail(m),
        "dimensions": md.get("Current Dimensions (in mm)", ""),
        "order": order,
        "institution": ", ".join(x for x in (md.get("Location"), COLLECTIONS.get(md.get("Collection Name"), md.get("Collection Name"))) if x),
        "shelfmark": md.get("Shelfmark", ""),
        "catalogue_title": title,
        "catalogue_date": md.get("Date of origin", "not given"),
        "status": "unidentified",
        "confidence": "none",
        "identification": "Not identified",
        "note": PLACEHOLDER,
        "verify": record,
        "examined": today,
        "identified_on": None,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--cache", help="acquire_batch.py --output directory (default: the shared image cache)")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    a = ap.parse_args()
    if not a.cache:
        import iiif
        a.cache = str(iiif.cache_dir())
    data = json.load(open(DATA, encoding="utf-8"))
    have = {r["id"] for r in data}
    order = max(r["order"] for r in data)
    for fid in a.ids:
        if fid in have:
            print(fid, "already registered")
            continue
        order += 1
        data.append(row(fid, a.cache, order, a.date))
        print(fid, "registered as", order)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
