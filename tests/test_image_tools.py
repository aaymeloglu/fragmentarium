"""Local crop geometry, GW reproduction-link parsing and Google Books search-inside parsing."""
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


def test_gbwithin_reads_page_numbers_and_builds_exact_volume_query():
    gb = load("gbwithin")
    response = {"number_of_results": 2, "search_results": [
        {"page_id": "PA9", "page_number": "9", "snippet_text": "... nec ad oculum  nec ad intellectum ..."},
        {"page_id": "PP3", "snippet_text": "front matter"}]}
    assert gb.hits(response) == [("9", "... nec ad oculum nec ad intellectum ..."), ("", "front matter")]
    assert gb.hits({"number_of_results": 0}) == []
    u = gb.url("tWdJAAAAYAAJ", '"ad oculum"')
    assert "id=tWdJAAAAYAAJ" in u and "q=%22ad+oculum%22" in u and "jscmd=SearchWithinVolume2" in u


def test_bnf_manifest_addresses_are_rewritten_to_the_api_host():
    iiif = load("iiif")
    base, ext, scale = iiif.image_base("https://gallica.bnf.fr/iiif/ark:/12148/btv1b84386681/f219")
    assert base == "https://openapi.bnf.fr/iiif/image/v3/ark:/12148/btv1b84386681/f219"
    assert ext == "default.jpg" and scale == 1.0
    other = "https://fragmentarium.ms/loris/F-z56d/x.jp2"
    assert iiif.image_base(other) == (other, "default.jpg", 2.0)


def test_tilepacket_grid_covers_box_with_overlap():
    tp = load("tilepacket")
    tiles = tp.grid((100, 200, 1100, 2200), cols=2, rows=4, overlap=0.1)
    assert len(tiles) == 8
    assert min(t[0] for t in tiles) == 100 and max(t[2] for t in tiles) == 1100
    assert min(t[1] for t in tiles) == 200 and max(t[3] for t in tiles) == 2200
    assert tiles[0][2] > tiles[1][0], "neighbouring columns must share pixels"
    assert tiles[0][3] > tiles[2][1], "neighbouring rows must share lines"
    for bad in (dict(cols=0, rows=1), dict(cols=1, rows=1, overlap=1.0)):
        with pytest.raises(ValueError):
            tp.grid((0, 0, 10, 10), **bad)
    with pytest.raises(ValueError):
        tp.grid((5, 0, 5, 10), 1, 1)


def test_schneyer_query_is_scoped_to_one_volume_and_highlights_are_flattened():
    sch = load("schneyer")
    u = sch.url('"ter flevit"', "repertoriumderla0004schn")
    assert "identifier%3Arepertoriumderla0004schn" in u and "%22ter%20flevit%22" in u
    response = {"hits": {"hits": [{"highlight": {"text": ["a  {{{ter flevit}}}\n b", "c"]}}, {}]}}
    assert sch.highlights(response) == ["a {{{ter flevit}}} b", "c"]
    assert sch.highlights({}) == []
    assert len(sch.VOLUMES) == 9


def test_hspsearch_rows_carry_digital_links_and_matched_passages():
    hsp = load("hspsearch")
    assert "q=%22De+regiminibus%22" in hsp.url('"De regiminibus"')
    response = {"metadata": {"highlighting": {"d1": {"text": ["Sermones  <em>Ungarus</em>\n f. 55r"]}}},
                "payload": [{"hspObject": {"id": "o1", "settlement-display": "Leipzig", "repository-display": "UB",
                                           "idno-display": "Ms 720", "orig-date-lang-display": "13. Jh."},
                             "hspDescriptions": [{"id": "d1"}],
                             "hspDigitizeds": [{"manifest-url-display": "https://example.org/manifest.json"}, {}]}]}
    assert hsp.rows(response) == [("Leipzig", "UB", "Ms 720", "13. Jh.", ["https://example.org/manifest.json"],
                                   ["Sermones Ungarus f. 55r"])]
    assert hsp.rows({}) == []
