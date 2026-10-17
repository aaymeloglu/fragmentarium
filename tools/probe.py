#!/usr/bin/env python3
"""Measure whether a record's images carry readable text, and cut a reading-size sample of it.

    uv run --group images python tools/probe.py F-xxxx OUTDIR [--canvas N] [--samples 1] [--enhance]
    uv run --group images python tools/probe.py --local IMAGE OUTDIR      # an image already on disk

A contact sheet or a 1600 px overview is too small to judge small script: a near-blank strip and a
legible one look alike, and a few lines of small cursive look like noise. This finds the objects
on each canvas (parchment, paper, ruler, colour chart) against the photographic background,
measures each object's text lines from the periodicity of its ink rows, and cuts a sample of
about fifteen lines at native resolution from the object's most regular text band.

For each object it prints the native box, the size, the text orientation (rows: lines run across;
cols: the text is sideways), the line pitch in native pixels, an estimated line count, a
periodicity score (0-1; under about 0.2 there are no regular lines, as on a ruler, a blank or a
washed leaf) and an ink contrast (0-1; under about 0.1 the text, if any, is very faint). The
numbers rank objects and records for a reader; they do not replace looking: the sample shows
whether the lines are letters. Objects are listed most text-like first; strongly coloured objects
(colour charts, marbled or painted covers) are tagged and ranked down, and a long object with ticks
across it is tagged as possibly the ruler but still sampled, since a strip with sideways text looks
the same. A strip pasted on a coloured cover is found as part of the cover: point at it with --box.
--flip mirrors the samples of an offset (h: mirror image; v: mirror image upside down). --enhance adds a contrast-stretched, sharpened copy of each
sample for faint ink (an aid to viewing, not evidence). A JSON summary goes to OUTDIR.
Needs Pillow and numpy (group `images`).
"""
import argparse
import io
import json
import sys
from pathlib import Path

GRID = 240  # width of the downscaled image in which objects are found
COLOURFUL = 0.35  # mean saturation above which an object is likely a colour chart or decorated cover
MAX_SAMPLE = 2200  # native pixels across a sample; wider is shrunk past reading size when viewed


def load(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gray(im):
    """The green channel: black, brown and red inks are all dark in it, so red text is measured too."""
    import numpy as np
    return np.asarray(im.convert("RGB"), dtype=np.float32)[:, :, 1]


def otsu(a):
    import numpy as np
    hist, edges = np.histogram(a, bins=64, range=(0, 255))
    p = hist / max(hist.sum(), 1)
    w = np.cumsum(p)
    mu = np.cumsum(p * edges[:-1])
    between = (mu[-1] * w - mu) ** 2 / np.maximum(w * (1 - w), 1e-9)
    return float(edges[int(np.argmax(between))])


def objects(g, min_frac=0.004):
    """Boxes (x0, y0, x1, y1, in g's pixels) of the bright or dark objects that differ from the border."""
    import numpy as np
    t = otsu(g)
    border = np.concatenate([g[0], g[-1], g[:, 0], g[:, -1]])
    mask = g > t if border.mean() <= t else g < t  # objects are the class the border is not
    h, w = mask.shape
    seen = np.zeros_like(mask)
    out = []
    for y0 in range(h):
        for x0 in range(w):
            if not mask[y0, x0] or seen[y0, x0]:
                continue
            stack, n, box = [(y0, x0)], 0, [x0, y0, x0, y0]
            seen[y0, x0] = True
            while stack:
                y, x = stack.pop()
                n += 1
                box = [min(box[0], x), min(box[1], y), max(box[2], x), max(box[3], y)]
                for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
            if n >= min_frac * h * w:
                out.append((box[0], box[1], box[2] + 1, box[3] + 1, n))
    return sorted(out, key=lambda b: -b[4])


def detrend(profile, window=41):
    """Remove slow changes (stains, lighting, curvature) and stroke-scale noise from an ink profile."""
    import numpy as np
    if len(profile) < 3:
        return profile - profile.mean()
    k = min(window, len(profile) // 2 * 2 - 1)
    slow = np.convolve(profile, np.ones(k) / k, mode="same")
    p = profile - slow
    return np.convolve(p, np.ones(3) / 3, mode="same")


def period(profile, lo=10, hi=None):
    """(pitch, score) of the strongest repetition in a 1-D ink profile: the highest local peak of its
    autocorrelation between lags lo and hi. score 0 means no peak, i.e. no regular lines."""
    import numpy as np
    p = detrend(np.asarray(profile, dtype=np.float64))
    if len(p) < 3 * lo or not p.any():
        return 0.0, 0.0
    ac = np.correlate(p, p, "full")[len(p) - 1:]
    if ac[0] <= 0:
        return 0.0, 0.0
    ac = ac / ac[0]
    hi = min(hi or len(p) // 3, len(ac) - 2)
    peaks = [k for k in range(max(lo, 1), hi + 1) if ac[k] > ac[k - 1] and ac[k] >= ac[k + 1] and ac[k] > 0]
    if not peaks:
        return 0.0, 0.0
    best = max(peaks, key=lambda k: ac[k])
    # prefer the fundamental: a peak near half the lag that is nearly as strong is the true pitch
    near = [k for k in peaks if abs(k - best / 2) <= 2 and ac[k] > 0.8 * ac[best]]
    if near:
        best = near[0]
    return float(best), float(ac[best])


def measure(g):
    """Text measurements of one object's grey image: orientation, pitch (pixels), lines, scores, contrast.
    Lines are taken as horizontal unless the sideways reading is clearly more regular."""
    import numpy as np
    ink = 255.0 - g
    lo, hi = np.percentile(g, 5), np.percentile(g, 95)
    contrast = float((hi - lo) / 255.0)
    rp, rs = period(ink.mean(axis=1))
    cp, cs = period(ink.mean(axis=0))
    if cs > rs + 0.15:
        orient, pitch, score, length = "cols", cp, cs, g.shape[1]
    else:
        orient, pitch, score, length = "rows", rp, rs, g.shape[0]
    lines = int(length / pitch) if pitch else 0
    return {"orient": orient, "pitch": pitch, "lines": lines, "score": round(score, 3),
            "score_rows": round(rs, 3), "score_cols": round(cs, 3), "contrast": round(contrast, 3)}


def best_band(g, orient, pitch, lines=15):
    """Start and length (pixels along the line axis) of the band to sample: the most regular run of about
    `lines` lines, or, when no line pitch was found, the inkiest band about as long as the object is wide."""
    import numpy as np
    prof = (255.0 - g).mean(axis=1 if orient == "rows" else 0)
    n = len(prof)
    cross = g.shape[1 if orient == "rows" else 0]
    span = int(min(n, pitch * lines)) if pitch else int(min(n, max(cross, n // 4)))
    if span >= n or span < 1:
        return 0, n
    step = max(1, int(pitch) if pitch else span // 8)
    best, start = -1.0, 0
    for s in range(0, n - span + 1, step):
        var = float(prof[s:s + span].std())
        sc = period(prof[s:s + span], lo=max(3, int(pitch * 0.6)), hi=int(pitch * 1.6))[1] if pitch else 1.0
        if sc * var > best:
            best, start = sc * var, s
    return start, span


def inkiest_window(g, orient, width):
    """Start of the `width`-pixel window across the lines with the most ink variation (text, not margin)."""
    import numpy as np
    prof = (255.0 - g).std(axis=0 if orient == "rows" else 1)
    n = len(prof)
    if width >= n:
        return 0
    c = np.convolve(prof, np.ones(width), mode="valid")
    return int(np.argmax(c))


def saturation(im):
    """Mean colour saturation (0-1). Parchment and paper are near-neutral; colour charts and marbled or
    painted covers are strongly coloured."""
    import numpy as np
    return float(np.asarray(im.convert("HSV"), dtype=np.float32)[:, :, 1].mean() / 255.0)


def flipped(im, flip):
    from PIL import ImageOps
    if flip in ("h", "hv"):
        im = ImageOps.mirror(im)
    if flip in ("v", "hv"):
        im = ImageOps.flip(im)
    return im


def enhance(im):
    from PIL import ImageEnhance, ImageOps
    return ImageEnhance.Sharpness(ImageOps.autocontrast(im.convert("L"), cutoff=1)).enhance(1.6)


def probe_image(full, region, native_w, native_h, outdir, stem, samples=1, enh=False, min_frac=0.004, flip=None,
                only=None):
    """Probe one canvas. `full(w)` returns the whole image at width w; `region(box, w)` a native box at width w.
    Objects come back most text-like first (regular lines, contrast, not strongly coloured)."""
    small = full(GRID)
    sx = native_w / small.size[0]
    sy = native_h / small.size[1]
    res = []
    if only is not None:  # a caller-given native box replaces object finding
        found = [(int(only[0] / sx), int(only[1] / sy), max(int(only[0] / sx) + 1, int(only[2] / sx)),
                  max(int(only[1] / sy) + 1, int(only[3] / sy)), 0)]
    else:
        found = objects(gray(small), min_frac)
    for k, (x0, y0, x1, y1, _) in enumerate(found):
        box = tuple(only) if only is not None else (int(x0 * sx), int(y0 * sy), min(native_w, int(x1 * sx)), min(native_h, int(y1 * sy)))
        bw, bh = box[2] - box[0], box[3] - box[1]
        view_w = min(bw, 1600)
        view = region(box, view_w)
        g = gray(view)
        m = measure(g)
        m["saturation"] = round(saturation(view), 3)
        m["colourful"] = m["saturation"] > COLOURFUL
        f = bw / g.shape[1]
        m.update({"object": k, "box": list(box), "size": [bw, bh], "pitch": round(m["pitch"] * f, 1)})
        m["ruler"] = bool(max(bw, bh) > 4 * min(bw, bh) and m["score_cols" if bw > bh else "score_rows"] > m["score"] - 1e-9
                          and m["orient"] == ("cols" if bw > bh else "rows"))
        m["samples"] = []
        # a ruler-like object is still sampled: a narrow strip with sideways text looks like a ruler here
        pitch_view = m["pitch"] / f if m["score"] >= 0.15 else 0
        start, span = best_band(g, m["orient"], pitch_view)
        across = int(min(MAX_SAMPLE / f, g.shape[1] if m["orient"] == "rows" else g.shape[0]))
        for j in range(samples):
            a0, a1 = start + j * span, start + (j + 1) * span
            if a0 >= (g.shape[0] if m["orient"] == "rows" else g.shape[1]):
                break
            band = g[a0:a1] if m["orient"] == "rows" else g[:, a0:a1]
            c0 = inkiest_window(band, m["orient"], across)
            if m["orient"] == "rows":
                nb = (box[0] + int(c0 * f), box[1] + int(a0 * f), box[0] + int((c0 + across) * f), min(box[3], box[1] + int(a1 * f)))
            else:
                nb = (box[0] + int(a0 * f), box[1] + int(c0 * f), min(box[2], box[0] + int(a1 * f)), box[1] + int((c0 + across) * f))
            nb = (nb[0], nb[1], min(nb[2], box[2]), min(nb[3], box[3]))
            if nb[2] <= nb[0] or nb[3] <= nb[1]:
                break
            img = flipped(region(nb, min(nb[2] - nb[0], MAX_SAMPLE)), flip)
            p = Path(outdir) / f"{stem}_o{k}_s{j}.jpg"
            img.convert("RGB").save(p, quality=90)
            entry = {"file": str(p), "box": list(nb)}
            if enh:
                q = Path(outdir) / f"{stem}_o{k}_s{j}_enh.jpg"
                enhance(img).save(q, quality=90)
                entry["enhanced"] = str(q)
            m["samples"].append(entry)
        m["rank"] = round(m["score"] * m["contrast"] * (0.3 if m["colourful"] else 1.0) * (0.5 if m["ruler"] else 1.0), 4)
        res.append(m)
    return sorted(res, key=lambda m: -m["rank"])


def iiif_fns(c):
    from PIL import Image
    iiif = load("iiif")
    Image.MAX_IMAGE_PIXELS = None

    def get(url):
        return Image.open(io.BytesIO(iiif.get(url, timeout=180)))

    def full(w):
        return get(f"{c['base']}/full/{w},/0/{c['ext']}")

    def region(box, w):
        x0, y0, x1, y1 = box
        w = int(min(w, (x1 - x0) * c["max_scale"]))
        return get(f"{c['base']}/{x0},{y0},{x1 - x0},{y1 - y0}/{w},/0/{c['ext']}")
    return full, region


def local_fns(path):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(path)

    def full(w):
        return im.resize((w, max(1, round(im.size[1] * w / im.size[0]))))

    def region(box, w):
        c = im.crop(box)
        return c.resize((w, max(1, round(c.size[1] * w / c.size[0])))) if w != c.size[0] else c
    return im.size, full, region


def report(label, res):
    for m in res:
        print(f"  {label} obj{m['object']} box {','.join(map(str, m['box']))} size {m['size'][0]}x{m['size'][1]} "
              f"{m['orient']} pitch {m['pitch']} lines~{m['lines']} score {m['score']} "
              f"(rows {m['score_rows']}, cols {m['score_cols']}) contrast {m['contrast']}"
              + ("  [long object with ticks across it: the ruler, or a strip with sideways text]" if m["ruler"] else "")
              + ("  [strongly coloured: colour chart or decorated cover?]" if m["colourful"] else ""))
        for s in m["samples"]:
            print(f"      sample {s['file']} native box {','.join(map(str, s['box']))}"
                  + (f" enhanced {s['enhanced']}" if "enhanced" in s else ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="F-id, or an image path with --local")
    ap.add_argument("outdir")
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--canvas", type=int)
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--enhance", action="store_true")
    ap.add_argument("--box", help="x0,y0,x1,y1 native pixels: probe this area only (a strip on a coloured or "
                    "marbled cover is not separated from the cover by object finding); use with --canvas")
    ap.add_argument("--flip", choices=("h", "v", "hv"),
                    help="mirror the samples for an offset (h: mirror image; v: mirror image upside down)")
    a = ap.parse_args(argv)
    only = tuple(int(v) for v in a.box.split(",")) if a.box else None
    if only and not (a.local or a.canvas is not None):
        ap.error("--box needs --canvas (or --local)")
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    summary = {}
    if a.local:
        (w, h), full, region = local_fns(a.target)
        res = probe_image(full, region, w, h, out, Path(a.target).stem, a.samples, a.enhance, flip=a.flip, only=only)
        report(Path(a.target).name, res)
        summary[a.target] = res
    else:
        iiif = load("iiif")
        cs = iiif.canvases(a.target)
        sel = [a.canvas] if a.canvas is not None else range(len(cs))
        for i in sel:
            c = cs[i]
            if not iiif.usable(i, c) or not (c["w"] and c["h"]):
                continue
            full, region = iiif_fns(c)
            try:
                res = probe_image(full, region, c["w"], c["h"], out, f"{a.target}_c{i}", a.samples, a.enhance, flip=a.flip, only=only)
            except Exception as e:  # one bad canvas should not stop the record
                print(f"canvas {i} ({c['label']}): {e}", file=sys.stderr)
                continue
            print(f"canvas {i} {c['label']} {c['w']}x{c['h']}")
            report(f"c{i}", res)
            summary[str(i)] = {"label": c["label"], "objects": res}
    (out / f"{Path(a.target).stem}-probe.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
