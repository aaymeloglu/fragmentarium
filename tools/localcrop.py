#!/usr/bin/env python3
"""Cut reading crops from an image that is already on disk.

    uv run --group images python tools/localcrop.py SRC OUT x0,y0,x1,y1 [--width N] [--rotate 180] [--autocontrast]
                                                    [--channel b] [--equalize]
    uv run --group images python tools/localcrop.py SRC OUTDIR --strips 6 [--columns 2] [--overlap 0.08] [--width 1700]

`tools/iiif.py` asks the library server for a region; this works on a cached native download,
which is quicker when reading a whole leaf and is the only option when the server refuses
region requests. Coordinates are native pixels of SRC (x0,y0 upper left, x1,y1 lower right).
--width enlarges or reduces the crop for viewing only: it adds no evidence, so cite the native
coordinates, not the output size. For faded iron-gall ink, --channel b --equalize (the blue channel,
histogram-equalised) can recover lines that greyscale --autocontrast cannot. --strips cuts each column into overlapping horizontal bands
of roughly ten to twenty lines, the size at which small cursive stays legible to an image reader.
Every output prints its native box so a reading can be relocated. Needs Pillow (group `images`).
"""
import argparse
from pathlib import Path


def boxes(width, height, strips, columns=1, overlap=0.08):
    """Native-pixel boxes covering the image: `columns` across, `strips` down, bands overlapping."""
    if strips < 1 or columns < 1 or not 0 <= overlap < 1:
        raise ValueError("strips and columns must be positive; overlap in [0, 1)")
    out = []
    cw, sh = width / columns, height / strips
    for c in range(columns):
        x0, x1 = round(max(0, c * cw - cw * overlap / 2)), round(min(width, (c + 1) * cw + cw * overlap / 2))
        for s in range(strips):
            y0, y1 = round(max(0, s * sh - sh * overlap / 2)), round(min(height, (s + 1) * sh + sh * overlap / 2))
            out.append((c, s, (x0, y0, x1, y1)))
    return out


def cut(im, box, width=None, rotate=0, autocontrast=False, channel=None, equalize=False):
    from PIL import Image, ImageOps
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= im.size[0] and 0 <= y0 < y1 <= im.size[1]):
        raise ValueError(f"box {box} is outside the {im.size[0]}x{im.size[1]} image")
    c = im.crop(box)
    if rotate:
        c = c.rotate(-rotate, expand=True)
    if channel:
        c = c.convert("RGB").getchannel(channel.upper())
    if equalize:
        c = ImageOps.equalize(c)
    if autocontrast:
        c = ImageOps.autocontrast(c if channel else c.convert("RGB"), cutoff=1)
    if width:
        c = c.resize((width, max(1, round(c.size[1] * width / c.size[0]))), Image.LANCZOS)
    return c


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("out", help="output file, or directory with --strips")
    ap.add_argument("box", nargs="?", help="x0,y0,x1,y1 in native pixels")
    ap.add_argument("--strips", type=int)
    ap.add_argument("--columns", type=int, default=1)
    ap.add_argument("--overlap", type=float, default=0.08)
    ap.add_argument("--width", type=int)
    ap.add_argument("--rotate", type=int, default=0, choices=(0, 90, 180, 270), help="clockwise degrees")
    ap.add_argument("--autocontrast", action="store_true")
    ap.add_argument("--channel", choices=("r", "g", "b"), help="read one colour channel (b helps faded ink)")
    ap.add_argument("--equalize", action="store_true", help="histogram-equalise the crop")
    a = ap.parse_args(argv)
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(a.src)
    if a.strips:
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        for c, s, box in boxes(*im.size, a.strips, a.columns, a.overlap):
            p = out / f"col{c + 1}-strip{s + 1:02d}.jpg"
            cut(im, box, a.width, a.rotate, a.autocontrast, a.channel, a.equalize).save(p, quality=90)
            print(p, "native box", ",".join(map(str, box)))
    else:
        if not a.box:
            ap.error("give x0,y0,x1,y1 or --strips")
        box = tuple(int(v) for v in a.box.split(","))
        cut(im, box, a.width, a.rotate, a.autocontrast, a.channel, a.equalize).save(a.out, quality=90)
        print(a.out, "native box", ",".join(map(str, box)), "of", "x".join(map(str, im.size)))


if __name__ == "__main__":
    main()
