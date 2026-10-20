import json
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlsplit
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import cantus_melody as melody


def test_web_keyboard_semantics_and_explicit_search_settings():
    assert melody.pitches('1--ddC---f--7g--hG--5') == '1-d-c-f-g-h-g'
    query = parse_qs(urlsplit(melody.search_url('searchmelody', 'dcfghg', transpose=True)).query)
    assert query['start'] == ['0'] and query['transpose'] == ['1']
    assert query['t'] == ['1-d-c-f-g-h-g']


@pytest.mark.parametrize('value', ['abc', 'dddddd', 'abcdefghi', 'd-f-6--h-g', 'd-f-?-g-h', 'dfghx', 'abcdefghjklmnopq'])
def test_cannot_silently_bridge_missing_or_uncertain_notes(value):
    with pytest.raises(ValueError):
        melody.pitches(value)


def test_parse_both_live_response_shapes():
    for endpoint in melody.ENDPOINTS:
        body = (Path(__file__).parent / 'fixtures' / (endpoint + '.html')).read_text()
        result = melody.parse_results(body, endpoint)
        assert result['reported_count'] == result['returned_count'] == 1
        row = result['results'][0]
        assert row['volpiano'].startswith('1--')
        assert row['result_url'].startswith('https://')
        if endpoint.endswith('-con'):
            assert row['folio'] == '002r' and row['db'] == 'SEMM'
        else:
            assert row['label'] == '003133m1'


def test_unavailable_and_changed_layout_are_not_no_hits():
    with pytest.raises(ValueError, match='not a zero-result'):
        melody.parse_results('<html>Please log in</html>', 'searchmelody')
    zero = melody.parse_results('<h4>Cantus Index melodies (<b>0</b> melodies)</h4><table></table>', 'searchmelody')
    assert zero['reported_count'] == 0 and zero['results'] == []
    body = (Path(__file__).parent / 'fixtures/searchmelody.html').read_text().replace('<b>1</b> melodies', '<b>30</b> melodies')
    assert melody.parse_results(body, 'searchmelody')['truncated']


def test_partial_service_failure_is_explicit(monkeypatch, tmp_path):
    body = (Path(__file__).parent / 'fixtures/searchmelody.html').read_text()
    def fetch(url, cache, offline):
        if '/searchmelody-con?' in url:
            raise OSError('server unavailable')
        return body, {'url': url}
    monkeypatch.setattr(melody, 'fetch', fetch)
    result = melody.search('dcfghg', tmp_path, offline=True)
    assert not result['complete']
    assert result['indexes']['searchmelody']['returned_count'] == 1
    assert result['indexes']['searchmelody-con']['status'] == 'unavailable'


def test_offline_cache_integrity(tmp_path):
    url = melody.search_url('searchmelody', 'dcfghg')
    with pytest.raises(ValueError, match='not cached'):
        melody.fetch(url, tmp_path, offline=True)
    key = melody.hashlib.sha256(url.encode()).hexdigest()
    raw = b'<h4>Cantus Index melodies (<b>0</b> melodies)</h4>'
    (tmp_path / (key + '.html')).write_bytes(raw)
    (tmp_path / (key + '.json')).write_text(json.dumps({'url': url, 'sha256': melody.hashlib.sha256(raw).hexdigest()}))
    assert melody.fetch(url, tmp_path, offline=True)[0] == raw.decode()
    (tmp_path / (key + '.html')).write_bytes(b'changed')
    with pytest.raises(ValueError, match='cache changed'):
        melody.fetch(url, tmp_path, offline=True)
