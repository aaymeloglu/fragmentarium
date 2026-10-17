#!/usr/bin/env python3
"""Fetch a Fragmentarium fragment's images through IIIF, resolving each library's quirks.

    python3 tools/iiif.py F-ss0e info                 # canvases, sizes, working image base per canvas
    python3 tools/iiif.py F-ss0e overview OUTDIR      # every canvas at 1600 px wide
    python3 tools/iiif.py F-ss0e tiles OUTDIR [--canvas N] [--cols 2] [--rows 4] [--scale 2]
                                                      # cut canvas N into a grid of crops at native x scale
    python3 tools/iiif.py F-ss0e crop OUTDIR x,y,w,h [--canvas N] [--scale 2]

Quirks handled: Ghent (adore.ugent.be, libcatalog.ugent.be) manifests point at dead URLs and the working base is the
ExLibris service id inside the canvas; BnF manifests give gallica.bnf.fr/iiif addresses, which
answer scripts with 403, so they are rewritten to BnF's API host (openapi.bnf.fr, IIIF Image 3,
no upscaling); upscaling beyond about 2x is refused by most servers, so --scale is capped at 2.

A manifest can point several canvases at one image (the catalogue's fault, not the library's). The
canvases then look like different leaves in the record but download as the same picture. Such
canvases are corrected when the record's other images are numbered in step with their canvases and
the image at the expected number has exactly the size the manifest gives for that canvas; otherwise
they are marked as faults, `info` says so, and the fetching commands skip them.
Standard library only.
"""
import base64
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (fragmentarium tools)"}


GALLICA = "https://gallica.bnf.fr/iiif/"
BNF_API = "https://openapi.bnf.fr/iiif/image/v3/"


def image_base(base):
    """Working image-service base for a manifest's base: (base, file name, largest allowed scale)."""
    if base.startswith(GALLICA):
        return BNF_API + base[len(GALLICA):], "default.jpg", 1.0
    return base, "default.jpg", 2.0


def _token(base):
    """Decode an ExLibris image id (URL-quoted base64 JSON naming the stored file); None for other servers."""
    try:
        data = json.loads(base64.b64decode(urllib.parse.unquote(base.rsplit("/", 1)[1]) + "=="))
        return data if isinstance(data, dict) and isinstance(data.get("key"), str) else None
    except Exception:
        return None


def _numbered(base):
    """(sequence number in the stored file name, function building the base for another number), or None."""
    data = _token(base)
    found = re.search(r"_(\d{3,5})(_[A-Za-z]+\.\w+)$", data["key"]) if data else None
    if not found:
        return None
    width = len(found.group(1))

    def rebuilt(number):
        key = data["key"][:found.start(1)] + str(number).zfill(width) + found.group(2)
        packed = json.dumps({**data, "key": key}, separators=(",", ":")).encode()
        return base.rsplit("/", 1)[0] + "/" + urllib.parse.quote(base64.b64encode(packed).decode(), safe="")
    return int(found.group(1)), rebuilt


def get(url, timeout=60, tries=3, pause=2.0):
    """Bytes at `url`. Retries transient failures (Fragmentarium manifests sometimes answer 404 once and
    then work; servers throttle with 429/5xx). A server whose TLS certificate fails verification
    (dams.antwerpen.be) is fetched without verification, with a warning: the content is public images
    and catalogue data, and nothing is sent."""
    import ssl
    import time
    import urllib.error
    ctx = None
    for attempt in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout, context=ctx).read()
        except urllib.error.HTTPError as e:
            if e.code not in (404, 429, 500, 502, 503, 504) or attempt == tries - 1:
                raise
        except urllib.error.URLError as e:
            if isinstance(e.reason, ssl.SSLCertVerificationError) and ctx is None:
                print(f"warning: TLS certificate of {urllib.parse.urlsplit(url).netloc} failed verification; "
                      "fetching without verification", file=sys.stderr)
                ctx = ssl._create_unverified_context()
                continue
            if attempt == tries - 1:
                raise
        time.sleep(pause * (attempt + 1))


def image_size(base):
    info = json.loads(get(base + "/info.json"))
    return info.get("width"), info.get("height")


def resolve_duplicates(bases, sizes, probe=image_size):
    """Find canvases that share one image and correct those that can be verified.

    `bases` are the image bases in canvas order, `sizes` the (width, height) the manifest gives for
    each canvas. Returns (bases, notes): notes[i] is None for a sound canvas, a string starting
    "corrected" where the base was replaced, or one starting "FAULT" where the canvas shows another
    canvas's image and no verified replacement exists (when the file names give nothing to judge
    by, the first canvas using an image is left alone and the later ones are marked). A correction
    needs three things: the file
    names of the unshared images carry a number that runs in step with the canvas order; the shared
    one is out of step; and the image at the in-step number has the manifest's size for the canvas.
    """
    bases, notes = list(bases), [None] * len(bases)
    first = {}
    shared = {i for i, b in enumerate(bases) if first.setdefault(b, i) != i}
    shared |= {first[bases[i]] for i in shared}
    if not shared:
        return bases, notes
    parsed = [_numbered(b) for b in bases]
    offsets = {parsed[i][0] - i for i in range(len(bases)) if i not in shared and parsed[i]}
    offset = offsets.pop() if len(offsets) == 1 and len(bases) - len(shared) >= 3 else None
    for i in sorted(shared):
        if offset is not None and parsed[i] and parsed[i][0] == i + offset:
            continue  # this canvas is the rightful owner of the shared image
        if offset is None and first[bases[i]] == i:
            continue  # nothing to judge by: leave the first canvas that uses the image, flag the later ones
        owner = first[bases[i]] if first[bases[i]] != i else min(j for j in shared if bases[j] == bases[i] and j != i)
        notes[i] = f"FAULT: the manifest gives this canvas the same image as canvas {owner}; not the leaf it is labelled as"
        if offset is None or not parsed[i]:
            continue
        candidate = parsed[i][1](i + offset)
        try:
            size = tuple(probe(candidate))
        except Exception:
            continue
        if all(sizes[i]) and size == tuple(sizes[i]):
            notes[i] = (f"corrected: the manifest pointed at image {parsed[i][0]} (canvas {owner}'s); using image "
                        f"{i + offset}, whose size {size[0]}x{size[1]} matches the manifest's for this canvas")
            bases[i] = candidate
    return bases, notes


def manifest(fid):
    u = f"https://fragmentarium.ms/metadata/iiif/{fid}/manifest.json"
    return json.loads(get(u))


def canvases(fid):
    return canvases_of(manifest(fid))


def canvases_of(m, probe=image_size):
    """Working image base, size and any fault note for each canvas of a manifest (see module docstring)."""
    out = []
    for c in m["sequences"][0]["canvases"]:
        res = c["images"][0]["resource"]
        rid = res["@id"]
        svc = res.get("service")
        svc_id = svc.get("@id") if isinstance(svc, dict) else None
        if ("adore.ugent.be" in rid or "libcatalog.ugent.be" in rid) and svc_id:
            base = svc_id
        elif "/full/" in rid:
            base = rid.split("/full/")[0]
        else:
            base = svc_id or rid
        base, ext, max_scale = image_base(base)
        w, h = c.get("width"), c.get("height")
        if not (w and h):  # some manifests (e.g. Leuven lib.is) omit sizes; the image server's info.json has them
            try:
                w, h = probe(base)
            except Exception:
                pass
        out.append({"label": c.get("label"), "base": base, "ext": ext, "w": w, "h": h, "max_scale": max_scale})
    bases, notes = resolve_duplicates([c["base"] for c in out], [(c["w"], c["h"]) for c in out], probe)
    for c, base, note in zip(out, bases, notes):
        c["base"], c["note"] = base, note
    return out


def usable(i, c):
    """False, with a message on stderr, for a canvas whose image is known to be another canvas's."""
    if (c.get("note") or "").startswith("FAULT"):
        print(f"canvas {i} skipped. {c['note']}", file=sys.stderr)
        return False
    return True


def fetch(url, path):
    data = get(url, timeout=180)
    Path(path).write_bytes(data)
    return len(data)


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    fid, cmd = argv[0], argv[1]
    opts = {k.lstrip("-"): v for k, v in zip(argv[2:], argv[3:]) if k.startswith("--")}
    args = [a for a in argv[2:] if not a.startswith("--") and a not in opts.values()]
    run(fid, canvases(fid), cmd, argv, opts, args)


def run(fid, cs, cmd, argv, opts, args):
    """Carry out one command on a list of canvases; `fid` names the output files."""
    if cmd == "info":
        for i, c in enumerate(cs):
            print(i, c["label"], c["w"], "x", c["h"], c["base"][:100])
            if c["note"]:
                print("   ", c["note"])
        return
    out = Path(args[0])
    out.mkdir(parents=True, exist_ok=True)
    scale = min(float(opts.get("scale", 2)), 2.0)
    sel = [int(opts["canvas"])] if "canvas" in opts else range(len(cs))
    skipped = [i for i in sel if not usable(i, cs[i])]
    sel = [i for i in sel if i not in skipped]
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
                    n = fetch(f"{c['base']}/{x},{y},{tw},{th}/{int(tw * min(scale, c['max_scale']))},/0/{c['ext']}", p)
                    print(p, n, "bytes")
    elif cmd == "crop":
        x, y, w, h = (int(v) for v in args[1].split(","))
        for i in sel:
            c = cs[i]
            p = out / f"{fid}_c{i}_{x}_{y}_{w}x{h}.jpg"
            print(p, fetch(f"{c['base']}/{x},{y},{w},{h}/{int(w * min(scale, c['max_scale']))},/0/{c['ext']}", p), "bytes")
    else:
        sys.exit(__doc__)
    if skipped:
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
