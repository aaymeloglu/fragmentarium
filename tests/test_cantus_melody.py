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


@pytest.mark.parametrize('notes', ['dcfghg', '9q9q', 'jhjlkjhghjhf', '1--ddC---f--7g--hG--5'])
def test_placements_cover_keyboard_without_changing_intervals(notes):
    original = [melody.PITCHES.index(n) for n in melody.pitches(notes)[2::2]]
    placements = melody.pitch_placements(notes)
    assert len(placements) == len(melody.PITCHES) - (max(original) - min(original))
    assert len({query for _, query in placements}) == len(placements)
    assert dict(placements)[0] == melody.pitches(notes)
    for shift, query in placements:
        shifted = [melody.PITCHES.index(n) for n in query[2::2]]
        assert [b - a for a, b in zip(original, shifted)] == [shift] * len(original)
    assert '9' in placements[0][1]
    assert 'q' in placements[-1][1]


def zero_response(endpoint):
    label = 'Melodies in the Cantus Index network' if endpoint.endswith('-con') else 'Cantus Index melodies'
    return f'<h4>{label} (<b>0</b> melodies)</h4><table></table>'


def test_real_false_negative_recovered_by_exact_placements(monkeypatch, tmp_path):
    """The failed server-transposed query must recover both known source records."""
    fixtures = Path(__file__).parent / 'fixtures'
    captured = {
        ('searchmelody-con', 'lklnmlkjklkh'): 'cantus-exact-paratur.html',
        ('searchmelody-con', 'hghkjhgfghge'): 'cantus-exact-kyrie.html',
        ('searchmelody', 'hghkjhgfghge'): 'cantus-exact-catalogue.html',
    }
    calls = []

    def fetch(url, cache, offline):
        params = parse_qs(urlsplit(url).query)
        assert params['transpose'] == ['0']
        endpoint = urlsplit(url).path.lstrip('/')
        notes = params['t'][0][2::2]
        calls.append((endpoint, notes))
        filename = captured.get((endpoint, notes))
        return ((fixtures / filename).read_text() if filename else zero_response(endpoint)), {'url': url}

    monkeypatch.setattr(melody, 'fetch', fetch)
    result = melody.search('jhjlkjhghjhf', tmp_path, transpose=True, offline=True)
    assert result['complete'] and result['strategy'] == 'exact-pitch-placements'
    assert len(calls) == len(set(calls)) == 24
    network = result['indexes']['searchmelody-con']
    assert network['returned_count'] == 7 and network['reported_count'] is None
    assert result['indexes']['searchmelody']['returned_count'] == 1
    by_url = {row['result_url']: row for row in network['results']}
    assert by_url['https://cantusdatabase.org/chant/495687']['retrieved_by'] == [
        {'query': melody.pitches('lklnmlkjklkh'), 'shift': 2}]
    assert by_url['https://cantusdatabase.org/chant/644939']['retrieved_by'] == [
        {'query': melody.pitches('hghkjhgfghge'), 'shift': -1}]


def test_nonempty_results_do_not_short_circuit_and_duplicates_keep_provenance(monkeypatch, tmp_path):
    calls = []

    def fetch(url, cache, offline):
        params = parse_qs(urlsplit(url).query)
        assert {k: params[k] for k in ('start', 'transpose', 'text', 'genre', 'mode')} == {
            'start': ['1'], 'transpose': ['0'], 'text': ['Homo quidam'], 'genre': ['A'], 'mode': ['1']}
        calls.append(url)
        endpoint = urlsplit(url).path.lstrip('/')
        return (Path(__file__).parent / 'fixtures' / (endpoint + '.html')).read_text(), {'url': url}

    monkeypatch.setattr(melody, 'fetch', fetch)
    result = melody.search('dcfghg', tmp_path, start=True, transpose=True,
                           text='Homo quidam', genre='A', mode='1', offline=True)
    count = len(melody.pitch_placements('dcfghg'))
    assert len(calls) == count * 2
    for index in result['indexes'].values():
        assert index['returned_count'] == 1
        assert len(index['results'][0]['retrieved_by']) == count
        assert len(index['queries']) == count
        assert all(q['reported_count'] == 1 and q['request']['url'] in calls for q in index['queries'])


def test_placement_failure_and_truncation_keep_successful_candidates(monkeypatch, tmp_path):
    def fetch(url, cache, offline):
        params = parse_qs(urlsplit(url).query)
        if params['t'] == [melody.pitches('jhjlkjhghjhf')]:
            raise OSError('placement unavailable')
        endpoint = urlsplit(url).path.lstrip('/')
        body = (Path(__file__).parent / 'fixtures' / (endpoint + '.html')).read_text()
        if params['t'] == [melody.pitches('lklnmlkjklkh')]:
            body = body.replace('<b>1</b> melodies', '<b>200</b> melodies')
        return body, {'url': url}

    monkeypatch.setattr(melody, 'fetch', fetch)
    result = melody.search('jhjlkjhghjhf', tmp_path, transpose=True, offline=True)
    assert not result['complete']
    for index in result['indexes'].values():
        assert index['status'] == 'partial' and not index['complete']
        assert index['truncated'] and index['returned_count'] == 1
        failures = [q for q in index['queries'] if q.get('status') == 'unavailable']
        assert len(failures) == 1 and failures[0]['shift'] == 0
        assert failures[0]['error'] == 'placement unavailable'
        truncated = [q for q in index['queries'] if q.get('truncated')]
        assert len(truncated) == 1 and truncated[0]['reported_count'] == 200


def test_offline_placements_require_each_cached_response_and_reuse_exact_cache(monkeypatch, tmp_path):
    # Cache all exact requests, then remove one. No server-transposed cache is needed.
    def no_network(*args, **kwargs):
        pytest.fail('offline replay accessed the network or slept')

    monkeypatch.setattr(melody.urllib.request, 'urlopen', no_network)
    monkeypatch.setattr(melody.time, 'sleep', no_network)
    paths = []
    for endpoint in melody.ENDPOINTS:
        for _, query in melody.pitch_placements('dcfghg'):
            url = melody.search_url(endpoint, query)
            raw = zero_response(endpoint).encode()
            key = melody.hashlib.sha256(url.encode()).hexdigest()
            path = tmp_path / (key + '.html')
            path.write_bytes(raw)
            (tmp_path / (key + '.json')).write_text(json.dumps({
                'url': url, 'sha256': melody.hashlib.sha256(raw).hexdigest()}))
            paths.append(path)
    assert melody.search('dcfghg', tmp_path, transpose=True, offline=True)['complete']
    paths[0].unlink()
    result = melody.search('dcfghg', tmp_path, transpose=True, offline=True)
    assert not result['complete']
    assert result['indexes']['searchmelody']['status'] == 'partial'
    assert result['indexes']['searchmelody-con']['complete']


def test_cli_all_placements_unavailable_is_not_a_zero_result(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(sys, 'argv', ['cantus_melody.py', 'dcfghg', '--transpose',
                                    '--offline', '--cache', str(tmp_path)])
    with pytest.raises(SystemExit) as error:
        melody.main()
    assert error.value.code == 1
    captured = capsys.readouterr()
    assert 'exact pitch placements available' in captured.out
    assert 'unavailable: Query not cached' in captured.out
    assert 'this is not a negative result' in captured.err
