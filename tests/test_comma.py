import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import comma

ROOT = Path(__file__).resolve().parents[1]

# Semi-diplomatic HTR as CoMMA prints it: MUFI signs, combining tildes, no expansion.
WITNESS = ('Alii dicunt et melius quod sufficit auditorẽ impetrare infra constitucionis tempus. '
           '¶S pone ꝙ aꝑꝑet auditorẽ impetratu esse s non constat ꝙ ꝑ pͥncipalez aut ꝑ ꝓcuratore '
           'fuit obtentus. minquid sufficit. expͥmitur ad cuius instancia sit datus auditor. s simplr dr '
           'mandat dñs ppͣ magro bernardo hyspano ꝙ causam que u̾titur inter tales suꝑ tali re audiat et '
           'diffiniat si aũt solus appellatus est presens')
SCRAMBLED = ('diffiniat tales auditor datus instancia obtentus procuratore principalem constat '
             'impetratum auditorem apparet pone hyspano magistro mandat audiat')
UNRELATED = ('In principio erat uerbum et uerbum erat apud deum et deus erat uerbum. Beatus uir qui non '
             'abiit in consilio impiorum et in uia peccatorum non stetit')
QUERY = [{'fragment': 'F-test', 'passages': [
    {'text': 'sed pone quod apparet auditorem impetratum esse sed non'},
    {'text': 'constat per principalem an per procuratorem fuit obtentus'},
    {'text': 'ad cuius instanciam sit datus auditor'},
    {'text': 'mandat dominus papa magistro'},
    {'text': 'vertitur inter tales super tali re audiat et diffiniat'}]}]


def corpus(root, monkeypatch, docs):
    root.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps({'shelfmark': s, 'iiif_manifest': f'https://example.org/{i}/manifest.json',
                         'pages': 10, 'text': t}, ensure_ascii=False) for i, (s, t) in enumerate(docs)]
    data = ('\n'.join(lines) + '\n').encode()
    (root / 'parts_0000.jsonl').write_bytes(data)
    monkeypatch.setattr(comma, 'PARTS', {'parts_0000.jsonl': (len(data), hashlib.sha256(data).hexdigest())})
    monkeypatch.setattr(comma, 'MAX_RATE', 1.0)      # a toy corpus has no rare words by global rates
    return data


def test_htr_tokens_are_normalised_with_abbreviation_flags():
    assert comma.norm_token('auditorẽ') == ('auditore', True)
    assert comma.norm_token('ꝓcuratore') == ('procuratore', True)
    assert comma.norm_token('Vir') == ('uir', False)
    assert comma.norm_word('Iustitiæ') == 'iustitiae'
    assert comma.norm_word('ꝑ') == 'per'


def test_match_kinds_and_their_weights():
    lookup = comma.build_lookup([{'fragment': 'q', 'words': ['pestilentie', 'auditorem', 'procuratorem']}],
                                {'tokens': 10 ** 9, 'counts': {}})
    assert comma.match('pestilentie', False, lookup) == (((0, 0),), 1.0)
    assert comma.match('pestilentide', False, lookup)[1] == 0.8      # one extra letter
    assert comma.match('pestilentic', False, lookup)[1] == 0.8       # one wrong letter
    assert comma.match('auditore', True, lookup) == (((0, 1),), 0.6)  # abbreviated: prefix
    assert comma.match('auditore', False, lookup)[0] == ((0, 1),)    # unabbreviated: one letter short
    assert comma.match('procur', False, lookup) == (None, 0)          # a bare prefix needs a sign
    assert comma.match('qua', True, lookup)[0] is None


def test_common_and_stop_words_are_not_searched():
    lookup = comma.build_lookup([{'fragment': 'q', 'words': ['quod', 'secundum', 'diffiniat']}],
                                {'tokens': 10 ** 6, 'counts': {'secundum': 5000, 'diffiniat': 2}})
    assert set(lookup['weight']) == {'diffiniat'}


def test_chain_keeps_query_order():
    hits = [(0, 2, 1.0, 0, 1), (1, 0, 1.0, 2, 3), (2, 1, 1.0, 4, 5), (3, 3, 1.0, 6, 7)]
    score, chain = comma.best_chain(hits, [1, 1, 1, 1])
    assert score == 3 and [h[1] for h in chain] == [0, 1, 3]


def test_search_finds_abbreviated_witness_above_shuffled_null(tmp_path, monkeypatch):
    root = tmp_path / 'comma'
    corpus(root, monkeypatch, [('Reims 708', WITNESS), ('Scrambled', SCRAMBLED), ('Psalter', UNRELATED)])
    comma.build_index(root, workers=1, log=lambda *a, **k: None)
    assert comma.status(root)['state'] == 'installed'
    result = comma.search(root, comma.load_queries(passages=[p['text'] for p in QUERY[0]['passages']]),
                          workers=1, chunks=2, log=lambda *a, **k: None)
    hits = result['queries'][0]['hits']
    assert hits[0]['shelfmark'] == 'Reims 708'
    assert hits[0]['chain'] >= 12 and hits[0]['margin'] > 3
    assert all(h['shelfmark'] != 'Psalter' for h in hits)
    scrambled = [h for h in hits if h['shelfmark'] == 'Scrambled']
    assert not scrambled or scrambled[0]['chain'] < hits[0]['chain'] / 2
    found = comma.context(root, 'Reims 708', find='hyspano')[0]['found']
    assert found and 'hyspano' in comma.context(root, 'Reims 708', found[0], before=0, after=7)[0]['text']


def test_query_file_skips_unusable_records(tmp_path):
    path = tmp_path / 'q.json'
    path.write_text(json.dumps(QUERY + [{'fragment': 'F-none', 'usable': False, 'passages': [{'text': 'x y'}]}]))
    assert [q['fragment'] for q in comma.load_queries(path)] == ['F-test']
    nulls = comma.with_nulls(comma.load_queries(path))
    assert nulls[1]['fragment'] == 'F-test#null' and sorted(nulls[1]['words']) == sorted(nulls[0]['words'])


def test_install_states(tmp_path, monkeypatch):
    root = tmp_path / 'comma'
    assert comma.status(root)['state'] == 'absent'
    root.mkdir()
    (root / comma.DECLINED).write_text('no')
    assert comma.status(root)['state'] == 'declined'
    corpus(root, monkeypatch, [('A', WITNESS)])
    assert comma.status(root)['state'] == 'incomplete'
    monkeypatch.setattr(comma, 'PARTS', {**comma.PARTS, 'parts_0001.jsonl': (1, '0')})
    comma.build_index(root, workers=1, log=lambda *a, **k: None)
    assert comma.status(root)['state'] == 'partial'
    with pytest.raises(SystemExit):
        comma.search(tmp_path / 'elsewhere', [], log=lambda *a, **k: None)


class RangeHandler(BaseHTTPRequestHandler):
    body = b''

    def do_GET(self):
        start = int(self.headers.get('Range', 'bytes=0-')[6:].split('-')[0])
        self.send_response(206 if start else 200)
        self.end_headers()
        self.wfile.write(self.body[start:])

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    RangeHandler.body = os.urandom(3_000_000)
    httpd = ThreadingHTTPServer(('127.0.0.1', 0), RangeHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f'http://127.0.0.1:{httpd.server_port}/part', RangeHandler.body
    httpd.shutdown()


def test_download_resumes_and_verifies(tmp_path, server):
    url, body = server
    target = tmp_path / 'parts_0000.jsonl'
    (tmp_path / 'parts_0000.jsonl.part').write_bytes(body[:1_000_000])
    digest = hashlib.sha256(body).hexdigest()
    assert comma.download(url, target, len(body), digest, log=lambda *a: None) == 'downloaded'
    assert target.read_bytes() == body
    assert comma.download(url, target, len(body), digest, log=lambda *a: None) == 'present'


def test_download_rejects_wrong_hash_and_leaves_nothing(tmp_path, server):
    url, body = server
    target = tmp_path / 'parts_0000.jsonl'
    with pytest.raises(ValueError, match='sha256'):
        comma.download(url, target, len(body), '0' * 64, log=lambda *a: None)
    assert not target.exists() and not (tmp_path / 'parts_0000.jsonl.part').exists()


def test_fetch_needs_explicit_consent_and_decline_is_remembered(tmp_path):
    env = {**os.environ, 'FRAGMENTARIUM_COMMA_DIR': str(tmp_path / 'c')}
    run = lambda *a: subprocess.run([sys.executable, str(ROOT / 'tools' / 'comma.py'), *a],
                                    capture_output=True, text=True, env=env)
    refused = run('fetch')
    assert refused.returncode == 2 and '26.8 GB' in refused.stderr and 'ask first' in refused.stderr
    assert not (tmp_path / 'c').exists()
    assert run('fetch', '--parts', '6').stderr.count('2.1 GB') == 1
    assert run('decline').returncode == 0
    assert json.loads(run('status').stdout)['state'] == 'declined'
