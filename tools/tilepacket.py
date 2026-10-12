#!/usr/bin/env python3
"""Build neutral reading packets of overview plus reading-size tiles from an acquire_batch cache.

    uv run --group images python tools/tilepacket.py SPEC.json --cache /tmp/source-images \
        --packets /tmp/neutral-packets --work /tmp/tiles --mapping /tmp/mapping.json

A whole native image is too reduced, when a reader views it, for small script: the first reader
then reports gaps that are a property of the view, not of the leaf. This cuts each chosen text
area into a grid of overlapping native-pixel tiles, adds one reduced overview per canvas for
layout, and registers them as a packet with `readings.py packet` under a neutral name.

SPEC.json maps a fragment id to a list of areas, each
    [canvas, [x0, y0, x1, y1], columns, rows, rotate]
where the box is in fractions of the image (0-1), columns x rows is the grid over that box, and
rotate is 0, 90, 180 or 270 degrees counterclockwise (for sideways or upside-down leaves). Aim
for tiles of ten to twenty lines, one column wide. Tiles overlap their neighbours by --overlap.

The mapping file keeps, for each fragment, the packet path, the tile files in packet order and
one public source citation per image (IIIF URL, native box, rotation) ready for
`readings.py freeze --image-source`. Keep the mapping and the cache away from the reader.
Needs Pillow (dependency group `images`).
"""
import argparse
import glob
import json
import os
import subprocess
import sys


def grid(box, cols, rows, overlap=0.12):
    """Overlapping tile boxes (x0, y0, x1, y1) covering box, row by row, clipped to the box."""
    if cols < 1 or rows < 1 or not 0 <= overlap < 1:
        raise ValueError("cols and rows must be at least 1 and overlap in [0, 1)")
    x0, y0, x1, y1 = box
    if not (x0 < x1 and y0 < y1):
        raise ValueError("empty box")
    tw, th = (x1 - x0) / cols, (y1 - y0) / rows
    out = []
    for r in range(rows):
        for c in range(cols):
            out.append((max(x0, int(x0 + c * tw - overlap * tw)), max(y0, int(y0 + r * th - overlap * th)),
                        min(x1, int(x0 + (c + 1) * tw + overlap * tw)), min(y1, int(y0 + (r + 1) * th + overlap * th))))
    return out


def build(fid, areas, cache, work, packet, overlap, overview):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    acq = json.load(open(os.path.join(cache, fid, "acquisition.json")))
    os.makedirs(work, exist_ok=True)
    files, sources, seen = [], [], set()
    for n, (canvas, frac, cols, rows, rot) in enumerate(areas):
        src = acq["sources"][canvas]
        url, label = src["source"], src.get("label")
        im = Image.open(glob.glob(os.path.join(cache, fid, f"canvas-{canvas}-w*.jpg"))[0]).convert("RGB")
        w, h = im.size
        if (canvas, rot) not in seen:
            seen.add((canvas, rot))
            ov = im.rotate(rot, expand=True) if rot else im.copy()
            ov.thumbnail((overview, overview))
            p = os.path.join(work, f"c{canvas}-r{rot}-overview.jpg")
            ov.save(p, quality=90)
            files.append(p)
            sources.append(f"{url} (canvas {canvas}, {label}): whole image {w}x{h}"
                           + (f" rotated {rot} degrees counterclockwise and" if rot else "")
                           + f" reduced to {ov.size[0]}x{ov.size[1]} for layout")
        box = (int(frac[0] * w), int(frac[1] * h), int(frac[2] * w), int(frac[3] * h))
        for k, b in enumerate(grid(box, cols, rows, overlap)):
            tile = im.crop(b)
            if rot:
                tile = tile.rotate(rot, expand=True)
            p = os.path.join(work, f"a{n}-c{canvas}-x{b[0]}-y{b[1]}.jpg")
            tile.save(p, quality=92)
            files.append(p)
            sources.append(f"{url} (canvas {canvas}, {label}): native-pixel box {b[0]},{b[1]},{b[2]},{b[3]}"
                           + (f", rotated {rot} degrees counterclockwise" if rot else "")
                           + f"; unrotated grid position column {k % cols + 1} of {cols}, row {k // cols + 1} of {rows}")
    readings = os.path.join(os.path.dirname(os.path.abspath(__file__)), "readings.py")
    subprocess.run([sys.executable, readings, "packet", packet, *files], check=True, stdout=subprocess.DEVNULL)
    return {"packet": packet, "files": files, "sources": sources}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--cache", required=True, help="acquire_batch.py --output directory")
    ap.add_argument("--packets", required=True, help="new directory for packet-NN folders")
    ap.add_argument("--work", required=True, help="directory for the cut tiles")
    ap.add_argument("--mapping", required=True, help="JSON file to write (coordinator only)")
    ap.add_argument("--overlap", type=float, default=0.12)
    ap.add_argument("--overview", type=int, default=1800, help="longest side of the layout overview")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    mapping = {}
    for n, (fid, areas) in enumerate(spec.items(), 1):
        mapping[fid] = build(fid, areas, a.cache, os.path.join(a.work, fid),
                             os.path.join(a.packets, f"packet-{n:02d}"), a.overlap, a.overview)
        print(fid, f"packet-{n:02d}", len(mapping[fid]["files"]), "images")
    with open(a.mapping, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
