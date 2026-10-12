#!/usr/bin/env python3
"""Contact sheets of every image in a Fragmentarium record, for surveying before reading.

    uv run --group images python tools/contactsheet.py F-xxxx OUTDIR [--per-sheet 8] [--width 600]

A record can have dozens of images: many leaves, both faces, host-volume pages, covers. Reading
them one by one at full size is slow and loses the overview. This fetches each canvas reduced,
labels it with its canvas number and the catalogue's label, and lays the thumbnails out a few to a
sheet, so one look shows which images carry text, which are blank or belong to the host volume,
where headings and rubrics are, and which way up each leaf is. Use it to choose the handful of
areas worth reading at native size (`tools/iiif.py crop`, `tools/localcrop.py`).

A thumbnail is for layout only: do not transcribe from it. Canvases whose image the manifest gets
wrong (see `tools/iiif.py`) are shown as a labelled blank, not as another leaf's picture.
Needs Pillow (dependency group `images`).
"""
import argparse
import io
import os
import urllib.request

import iiif


def layout(count, per_sheet, columns):
    """Split `count` thumbnails into sheets: a list of lists of (index, column, row)."""
    sheets = []
    for start in range(0, count, per_sheet):
        sheets.append([(i, (i - start) % columns, (i - start) // columns)
                       for i in range(start, min(start + per_sheet, count))])
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fragment")
    ap.add_argument("outdir")
    ap.add_argument("--per-sheet", type=int, default=8)
    ap.add_argument("--columns", type=int, default=4)
    ap.add_argument("--width", type=int, default=600, help="thumbnail width in pixels")
    a = ap.parse_args()
    from PIL import Image, ImageDraw
    Image.MAX_IMAGE_PIXELS = None
    canvases = iiif.canvases(a.fragment)
    os.makedirs(a.outdir, exist_ok=True)
    label_h, gap, tallest = 34, 10, a.width * 2
    for n, sheet in enumerate(layout(len(canvases), a.per_sheet, a.columns), 1):
        thumbs = {}
        for i, _, _ in sheet:
            c = canvases[i]
            if (c.get("note") or "").startswith("FAULT"):
                thumbs[i] = "image fault: " + c["note"]
                continue
            try:
                url = f"{c['base']}/full/{a.width},/0/{c['ext']}"
                data = urllib.request.urlopen(urllib.request.Request(url, headers=iiif.UA), timeout=180).read()
                thumbs[i] = Image.open(io.BytesIO(data)).convert("RGB")
                thumbs[i].thumbnail((a.width, tallest))
            except Exception as error:
                thumbs[i] = f"not fetched: {error}"
        # Each row is as tall as its tallest thumbnail, so landscape openings do not leave blank bands.
        heights = {}
        for i, _, row in sheet:
            height = thumbs[i].height if not isinstance(thumbs[i], str) else a.width // 3
            heights[row] = max(heights.get(row, 0), height)
        tops, y = {}, gap
        for row in sorted(heights):
            tops[row] = y
            y += label_h + heights[row] + gap
        page = Image.new("RGB", (a.columns * (a.width + gap) + gap, y), "white")
        draw = ImageDraw.Draw(page)
        for i, col, row in sheet:
            x, top = gap + col * (a.width + gap), tops[row]
            draw.text((x, top + 4), f"canvas {i}: {canvases[i]['label']}", fill="black")
            if isinstance(thumbs[i], str):
                draw.rectangle((x, top + label_h, x + a.width, top + label_h + heights[row]), outline="red")
                draw.text((x + 8, top + label_h + 8), thumbs[i][:90], fill="red")
            else:
                page.paste(thumbs[i], (x, top + label_h))
        path = os.path.join(a.outdir, f"{a.fragment}_sheet-{n:02d}.jpg")
        page.save(path, quality=88)
        print(path, f"canvases {sheet[0][0]}-{sheet[-1][0]}", flush=True)


if __name__ == "__main__":
    main()
