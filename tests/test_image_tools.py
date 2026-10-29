"""Local crop geometry, GW reproduction-link parsing and Google Books search-inside parsing."""
import importlib.util
import json
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


def _exlibris(number):
    import base64, json, urllib.parse
    token = json.dumps({"key": f"INST/storage/aa/9100_2022_{number:04d}_MA.jpg", "rep_id": "1"}).encode()
    return "https://img.example/iiif/2/" + urllib.parse.quote(base64.b64encode(token).decode(), safe="")


def test_shared_image_is_corrected_only_when_the_expected_file_has_the_manifest_size():
    iiif = load("iiif")
    # Canvases 0-5; the manifest wrongly gives canvases 3 and 4 the image of canvas 0.
    bases = [_exlibris(n) for n in (1, 2, 3, 1, 1, 6)]
    sizes = [(100, 200), (300, 200), (300, 201), (300, 202), (300, 203), (300, 204)]
    on_server = {"INST/storage/aa/9100_2022_0004_MA.jpg": (300, 202), "INST/storage/aa/9100_2022_0005_MA.jpg": (999, 999)}
    fixed, notes = iiif.resolve_duplicates(bases, sizes, probe=lambda base: on_server[iiif._token(base)["key"]])
    assert notes[0] is None and fixed[0] == bases[0], "the rightful owner of the image is left alone"
    assert iiif._token(fixed[3]) == {"key": "INST/storage/aa/9100_2022_0004_MA.jpg", "rep_id": "1"}
    assert notes[3].startswith("corrected")
    assert fixed[4] == bases[4] and notes[4].startswith("FAULT"), "a size mismatch must not be 'corrected'"
    assert [notes[i] for i in (1, 2, 5)] == [None, None, None]


def test_shared_image_without_a_numbering_pattern_is_flagged_not_guessed():
    iiif = load("iiif")
    plain = ["https://lib.example/a.jp2", "https://lib.example/a.jp2", "https://lib.example/b.jp2"]

    def probe(base):
        raise AssertionError("nothing to probe when no replacement can be derived")
    fixed, notes = iiif.resolve_duplicates(plain, [(1, 1)] * 3, probe=probe)
    assert fixed == plain
    assert notes[0] is None and notes[1].startswith("FAULT") and notes[2] is None
    # Too few sound canvases to trust a pattern: flag, do not correct.
    few = [_exlibris(1), _exlibris(1), _exlibris(3)]
    fixed, notes = iiif.resolve_duplicates(few, [(1, 1)] * 3, probe=probe)
    assert fixed == few and notes[1].startswith("FAULT")


def test_distinct_images_need_no_probe_and_get_no_notes():
    iiif = load("iiif")

    def probe(base):
        raise AssertionError("must not contact the server when no image is shared")
    bases = [_exlibris(n) for n in (1, 2, 3)]
    assert iiif.resolve_duplicates(bases, [(1, 1)] * 3, probe=probe) == (bases, [None, None, None])


def test_contact_sheet_layout_covers_every_canvas_once():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))  # contactsheet imports its sibling iiif
    cs = load("contactsheet")
    sheets = cs.layout(19, per_sheet=8, columns=4)
    assert [len(s) for s in sheets] == [8, 8, 3]
    assert [i for s in sheets for i, _, _ in s] == list(range(19))
    assert sheets[0][5] == (5, 1, 1) and sheets[2][0] == (16, 0, 0)


BNF_RESULTS = '''<a href="recalculFacets.html?val=https://gallica.bnf.fr/ark:/12148/btv1b9068482p&amp;filtre=Dao" target="_parent">Latin 15972&nbsp;(1)</a>
<a href="recalculFacets.html?val=https://gallica.bnf.fr/ark:/12148/btv1b8479002m&amp;filtre=Dao" target="_parent">Latin 1597&nbsp;(1)</a>
<a title="Consulter ce r&eacute;sultat" href="./ark:/12148/cc764712" target="_blank">Latin 15972 . Sermons.</a>'''
BNF_MANIFEST = {'label': {'fr': ['BnF. Département des Manuscrits. Latin 15972']}, 'items': [
    {'label': {'fr': ['1r']}, 'width': 6850, 'height': 4650, 'items': [{'items': [{'body': {
        'id': 'https://openapi.bnf.fr/iiif/image/v3/ark:/12148/btv1b9068482p/f1/full/max/0/default.webp',
        'service': [{'id': 'https://openapi.bnf.fr/iiif/image/v3/ark:/12148/btv1b9068482p/f1'}]}}]}]}]}


def test_bnf_shelfmark_is_matched_whole_and_the_manifest_label_checked():
    bnf = load("bnf")
    assert bnf.identifiers('latin 15972', BNF_RESULTS) == ['btv1b9068482p']
    assert bnf.identifiers('Latin 159', BNF_RESULTS) == []
    asked = []

    def fetch(url):
        asked.append(url)
        return json.dumps(BNF_MANIFEST).encode() if 'manifest' in url else BNF_RESULTS.encode()
    assert bnf.resolve('Latin 15972', fetch)[0] == 'btv1b9068482p'
    assert not any(url.startswith('https://gallica.bnf.fr') for url in asked)
    with pytest.raises(SystemExit):
        bnf.resolve('Latin 1597', fetch)  # in the catalogue, but the manifest served names another shelfmark
    with pytest.raises(SystemExit):
        bnf.resolve('Latin 4', fetch)


def test_bnf_canvases_take_the_api_image_service_and_allow_no_upscaling():
    bnf = load("bnf")
    assert bnf.canvases_of(BNF_MANIFEST) == [{
        'label': '1r', 'base': 'https://openapi.bnf.fr/iiif/image/v3/ark:/12148/btv1b9068482p/f1',
        'ext': 'default.jpg', 'w': 6850, 'h': 4650, 'max_scale': 1.0, 'note': None}]


def _page(lines=30, pitch=40, width=900, ink=60, paper=225, sideways=False):
    """A synthetic leaf on a dark background: `lines` rows of dashed ink with the given pitch."""
    np = pytest.importorskip("numpy")
    Image = pytest.importorskip("PIL.Image")
    h = lines * pitch + 2 * pitch
    a = np.full((h, width), paper, dtype=np.uint8)
    rng = np.random.default_rng(1)
    for i in range(lines):
        y = pitch + i * pitch
        x = 40 + int(rng.integers(0, 30))
        while x < width - 60:
            n = int(rng.integers(8, 60))  # words of irregular length and spacing, as in script
            a[y:y + pitch // 3, x:x + n] = ink
            x += n + int(rng.integers(6, 20))
    canvas = np.full((h + 200, width + 200), 20, dtype=np.uint8)
    canvas[100:100 + h, 100:100 + width] = a
    if sideways:
        canvas = canvas.T.copy()
    return Image.fromarray(canvas).convert("RGB")


def _fns(im):
    def full(w):
        return im.resize((w, max(1, round(im.size[1] * w / im.size[0]))))

    def region(box, w):
        c = im.crop(box)
        return c.resize((w, max(1, round(c.size[1] * w / c.size[0])))) if w != c.size[0] else c
    return full, region


def test_probe_measures_line_pitch_and_cuts_a_sample(tmp_path):
    pr = load("probe")
    im = _page(lines=30, pitch=40)
    full, region = _fns(im)
    res = pr.probe_image(full, region, *im.size, tmp_path, "t", enh=True)
    leaf = max(res, key=lambda m: m["size"][0] * m["size"][1])
    assert leaf["orient"] == "rows" and abs(leaf["pitch"] - 40) <= 3
    assert 25 <= leaf["lines"] <= 36 and leaf["score"] > 0.3
    x0, y0, x1, y1 = leaf["samples"][0]["box"]
    assert 80 <= x0 and x1 <= im.size[0] - 80 and y1 - y0 <= 16 * 43
    assert Path(leaf["samples"][0]["enhanced"]).exists()


def test_probe_finds_sideways_text_and_reports_blank_as_irregular(tmp_path):
    pr = load("probe")
    im = _page(lines=30, pitch=40, sideways=True)
    full, region = _fns(im)
    leaf = max(pr.probe_image(full, region, *im.size, tmp_path, "s"), key=lambda m: m["size"][0] * m["size"][1])
    assert leaf["orient"] == "cols" and abs(leaf["pitch"] - 40) <= 3
    blank = _page(lines=30, pitch=40, ink=225)
    full, region = _fns(blank)
    leaf = max(pr.probe_image(full, region, *blank.size, tmp_path, "b"), key=lambda m: m["size"][0] * m["size"][1])
    assert leaf["score"] < 0.15 and leaf["samples"]


def test_probe_ranks_text_above_coloured_objects_and_honours_box_and_flip(tmp_path):
    np = pytest.importorskip("numpy")
    Image = pytest.importorskip("PIL.Image")
    pr = load("probe")
    leaf = np.asarray(_page(lines=30, pitch=40)).copy()
    h, w, _ = leaf.shape
    canvas = np.full((h, w + 500, 3), 20, dtype=np.uint8)
    canvas[:, :w] = leaf
    rng = np.random.default_rng(2)
    canvas[100:500, w + 100:w + 400] = rng.integers(0, 255, (400, 300, 3), dtype=np.uint8)  # colour chart
    canvas[100:500, w + 100:w + 400, 0] = 230
    im = Image.fromarray(canvas)
    full, region = _fns(im)
    res = pr.probe_image(full, region, *im.size, tmp_path, "c")
    assert res[0]["rank"] >= res[-1]["rank"] and not res[0]["colourful"]
    assert any(m["colourful"] for m in res)
    only = (200, 200, 600, 700)
    res = pr.probe_image(full, region, *im.size, tmp_path, "b", only=only, flip="h")
    assert len(res) == 1 and res[0]["box"] == list(only)
    x0, y0, x1, y1 = res[0]["samples"][0]["box"]
    sample = Image.open(res[0]["samples"][0]["file"])
    assert sample.size[0] == x1 - x0
    expected = im.crop((x0, y0, x1, y1)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    assert abs(np.asarray(sample, dtype=int) - np.asarray(expected, dtype=int)).mean() < 8


def test_iiif_get_retries_transient_errors_and_tolerates_bad_certificates(monkeypatch):
    import ssl
    import urllib.error
    iiif = load("iiif")
    calls = []

    class Resp:
        def read(self):
            return b"ok"

    def fake(req, timeout=None, context=None):
        calls.append(context)
        if len(calls) == 1:
            raise urllib.error.HTTPError(req.full_url, 404, "nf", {}, None)
        if len(calls) == 2:
            raise urllib.error.URLError(ssl.SSLCertVerificationError("bad cert"))
        return Resp()
    monkeypatch.setattr(iiif.urllib.request, "urlopen", fake)
    monkeypatch.setattr("time.sleep", lambda s: None)
    assert iiif.get("https://example.org/x", tries=3) == b"ok"
    assert calls[0] is None and calls[1] is None and calls[2] is not None

    def gone(req, timeout=None, context=None):
        raise urllib.error.HTTPError(req.full_url, 403, "no", {}, None)
    monkeypatch.setattr(iiif.urllib.request, "urlopen", gone)
    with pytest.raises(urllib.error.HTTPError):
        iiif.get("https://example.org/y")


def test_tilepacket_mirrors_offset_tiles(tmp_path):
    np = pytest.importorskip("numpy")
    Image = pytest.importorskip("PIL.Image")
    tp = load("tilepacket")
    cache = tmp_path / "cache" / "F-test"
    cache.mkdir(parents=True)
    a = np.zeros((40, 60, 3), dtype=np.uint8)
    a[:, :20] = 255  # bright left third
    Image.fromarray(a).save(cache / "canvas-0-w60.jpg", quality=100)
    (cache / "acquisition.json").write_text(json.dumps({"sources": [{"source": "https://example.org/i", "label": "1r"}]}))
    out = tp.build("F-test", [[0, [0, 0, 1, 1], 1, 1, 0, "mirror"]], str(tmp_path / "cache"),
                   str(tmp_path / "work"), str(tmp_path / "packet"), 0.0, 100)
    tile = np.asarray(Image.open(out["files"][1]).convert("L"), dtype=int)
    assert tile[:, -15:].mean() > 200 and tile[:, :15].mean() < 50, "the bright side must move to the right"
    assert "mirrored left to right" in out["sources"][1]


def test_image_cache_serves_crops_and_manifest_when_library_is_offline(tmp_path, monkeypatch):
    Image = pytest.importorskip("PIL.Image")
    iiif = load("iiif")
    monkeypatch.setenv("FRAGMENTARIUM_IMAGE_DIR", str(tmp_path / "cache"))
    assert iiif.cache_dir() == tmp_path / "cache"
    m = {"sequences": [{"canvases": [{"label": "1r", "width": 40, "height": 20, "images": [{"resource": {
        "@id": "https://img.example/iiif/a/full/full/0/default.jpg"}}]}]}]}
    monkeypatch.setattr(iiif, "get", lambda url, **kw: json.dumps(m).encode())
    assert iiif.manifest("F-test") == m  # saved for later
    cs = iiif.canvases("F-test")
    out = tmp_path / "out"
    calls = []
    monkeypatch.setattr(iiif, "fetch", lambda url, path: calls.append(url) or 0)
    iiif.run("F-test", cs, "crop", [], {"scale": "1"}, [str(out), "0,0,20,10"])
    assert len(calls) == 1  # not cached yet: asked the library
    monkeypatch.setattr(iiif, "fetch", lambda url, path: Image.new("RGB", (40, 20), "white").save(path) or 1)
    iiif.run("F-test", cs, "cache", [], {}, [])
    assert (tmp_path / "cache" / "F-test" / "canvas-0-w40.jpg").exists()

    def offline(url, **kw):
        raise OSError("library offline")
    monkeypatch.setattr(iiif, "get", offline)
    monkeypatch.setattr(iiif, "fetch", lambda url, path: pytest.fail("fetched despite the cache"))
    cs = iiif.canvases("F-test")  # manifest from the cache
    iiif.run("F-test", cs, "crop", [], {"scale": "2"}, [str(out), "0,0,20,10"])
    with Image.open(out / "F-test_c0_0_0_20x10.jpg") as im:
        assert im.size == (40, 20)
