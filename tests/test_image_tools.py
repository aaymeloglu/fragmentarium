"""Local crop geometry and GW reproduction-link parsing."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_strip_boxes_cover_image_and_overlap():
    lc = load("localcrop")
    bs = lc.boxes(7706, 11459, strips=6, columns=2, overlap=0.1)
    assert len(bs) == 12
    for col in (0, 1):
        ys = [b for c, _, b in bs if c == col]
        assert ys[0][1] == 0 and ys[-1][3] == 11459
        for a, b in zip(ys, ys[1:]):
            assert b[1] < a[3], "adjacent bands must share lines"
    xs = sorted({(b[0], b[2]) for _, _, b in bs})
    assert xs[0][0] == 0 and xs[-1][1] == 7706 and xs[1][0] < xs[0][1]
    for _, _, (x0, y0, x1, y1) in bs:
        assert 0 <= x0 < x1 <= 7706 and 0 <= y0 < y1 <= 11459


def test_strip_boxes_reject_bad_arguments():
    lc = load("localcrop")
    for kw in (dict(strips=0), dict(strips=2, columns=0), dict(strips=2, overlap=1.0)):
        with pytest.raises(ValueError):
            lc.boxes(100, 100, **kw)


def test_cut_respects_bounds_rotation_and_width():
    Image = pytest.importorskip("PIL.Image")
    lc = load("localcrop")
    im = Image.new("RGB", (400, 300), "white")
    im.putpixel((10, 20), (0, 0, 0))
    c = lc.cut(im, (0, 0, 200, 100))
    assert c.size == (200, 100) and c.getpixel((10, 20)) == (0, 0, 0)
    r = lc.cut(im, (0, 0, 200, 100), rotate=180)
    assert r.size == (200, 100) and r.getpixel((189, 79)) == (0, 0, 0)
    assert lc.cut(im, (0, 0, 200, 100), width=400).size == (400, 200)
    with pytest.raises(ValueError):
        lc.cut(im, (0, 0, 500, 100))


def test_gw_page_lists_scans_not_catalogue_plumbing():
    gw = load("gw")
    page = '''<html><head><title>GW. Incunable M32924</title></head><body>
      <b>M32924</b> Pharetra doctorum. [Strassburg: Johann Mentelin, nicht nach 1472]. 2&deg;
      Reproduktionen: <a href="http://daten.digitale-sammlungen.de/0007/bsb00078844/images/">M&uuml;nchen SB</a>
      <a href="https://gallica.bnf.fr/ark:/12148/bpt6k8713360t">Paris BN</a>. HC 12908.
      <a href="http://purl.org/dc/terms/">x</a><a href="https://d-nb.info/gnd/118783319">y</a>
      <a href="http://b-gwshow01.pk.de/docs/M32924.htm">z</a></body></html>'''
    heading, links = gw.parse(page)
    assert "Mentelin" in heading and "1472" in heading and "Reproduktionen" not in heading
    assert links == ["http://daten.digitale-sammlungen.de/0007/bsb00078844/images/",
                     "https://gallica.bnf.fr/ark:/12148/bpt6k8713360t"]
