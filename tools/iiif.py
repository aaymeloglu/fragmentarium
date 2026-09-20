#!/usr/bin/env python3
"""Fetch a Fragmentarium fragment's images through IIIF, resolving each library's quirks.

    python3 tools/iiif.py F-ss0e info                 # canvases, sizes, working image base per canvas
    python3 tools/iiif.py F-ss0e overview OUTDIR      # every canvas at 1600 px wide
    python3 tools/iiif.py F-ss0e tiles OUTDIR [--canvas N] [--cols 2] [--rows 4] [--scale 2]
                                                      # cut canvas N into a grid of crops at native x scale
    python3 tools/iiif.py F-ss0e crop OUTDIR x,y,w,h [--canvas N] [--scale 2]

Quirks handled: Ghent (adore.ugent.be) manifests point at dead URLs and the working base is the
ExLibris service id inside the canvas; BnF canvases resolve to Gallica (native.jpg); upscaling
beyond about 2x is refused by most servers, so --scale is capped at 2. Standard library only.
"""
import json
import sys
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (fragmentarium tools)"}


def manifest(fid):
    u = f"https://fragmentarium.ms/metadata/iiif/{fid}/manifest.json"
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))


def canvases(fid):
    m = manifest(fid)
    out = []
    for c in m["sequences"][0]["canvases"]:
        res = c["images"][0]["resource"]
        rid = res["@id"]
        svc = res.get("service")
        svc_id = svc.get("@id") if isinstance(svc, dict) else None
        if "adore.ugent.be" in rid and svc_id:
            base = svc_id
        elif "/full/" in rid:
            base = rid.split("/full/")[0]
        else:
            base = svc_id or rid
        ext = "native.jpg" if "gallica" in base else "default.jpg"
        w, h = c.get("width"), c.get("height")
        if not (w and h):  # some manifests (e.g. Leuven lib.is) omit sizes; the image server's info.json has them
            try:
                info = json.load(urllib.request.urlopen(urllib.request.Request(base + "/info.json", headers=UA), timeout=60))
                w, h = info.get("width"), info.get("height")
            except Exception:
                pass
        out.append({"label": c.get("label"), "base": base, "ext": ext, "w": w, "h": h})
    return out


def fetch(url, path):
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180).read()
    Path(path).write_bytes(data)
    return len(data)


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    fid, cmd = argv[0], argv[1]
    opts = {k.lstrip("-"): v for k, v in zip(argv[2:], argv[3:]) if k.startswith("--")}
    args = [a for a in argv[2:] if not a.startswith("--") and a not in opts.values()]
    cs = canvases(fid)
    if cmd == "info":
        for i, c in enumerate(cs):
            print(i, c["label"], c["w"], "x", c["h"], c["base"][:100])
        return
    out = Path(args[0])
    out.mkdir(parents=True, exist_ok=True)
    scale = min(float(opts.get("scale", 2)), 2.0)
    sel = [int(opts["canvas"])] if "canvas" in opts else range(len(cs))
    if cmd == "overview":
        for i in sel:
            c = cs[i]
            p = out / f"{fid}_c{i}_overview.jpg"
            print(p, fetch(f"{c['base']}/full/1600,/0/{c['ext']}", p), "bytes")
    elif cmd == "tiles":
        cols, rows = int(opts.get("cols", 2)), int(opts.get("rows", 4))
        for i in sel:
            c = cs[i]
            if not (c["w"] and c["h"]):
                print("canvas", i, "has no size in manifest; use crop with explicit coordinates")
                continue
            tw, th = c["w"] // cols, c["h"] // rows
            for r in range(rows):
                for k in range(cols):
                    x, y = k * tw, r * th
                    p = out / f"{fid}_c{i}_r{r}c{k}.jpg"
                    n = fetch(f"{c['base']}/{x},{y},{tw},{th}/{int(tw * scale)},/0/{c['ext']}", p)
                    print(p, n, "bytes")
    elif cmd == "crop":
        x, y, w, h = (int(v) for v in args[1].split(","))
        for i in sel:
            c = cs[i]
            p = out / f"{fid}_c{i}_{x}_{y}_{w}x{h}.jpg"
            print(p, fetch(f"{c['base']}/{x},{y},{w},{h}/{int(w * scale)},/0/{c['ext']}", p), "bytes")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
