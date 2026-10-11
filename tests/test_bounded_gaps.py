"""Bounded fragments retain every surviving span and its original provenance."""
import itertools
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import latin_search as latin


def query(parts, gaps, **kwargs):
    return {'anchors': [{'id': 'line-ends', 'variants': [dict(parts=parts, gaps=gaps,
            basis='test reading', **kwargs)]}]}


def search(text, q, **kwargs):
    return latin.search([{'id': 'test', 'source': 'test edition', 'text': text}], q, **kwargs)['documents'][0]


def test_gap_bounds_order_and_required_parts():
    q = query(['materia', 'anima'], [{'min': 3, 'max': 5}])
    text = 'materia x anima; materia anima; anima x materia; materia xxxx anima'
    hits = search(text, q)['hits']
    assert [h['text'] for h in hits] == ['materia x anima']
    assert hits[0]['gap_normalized_characters'] == [3]
    assert not search('materia x missing', q)['hits']


def test_original_segments_survive_normalization_and_ocr_tolerance():
    raw = 'MATERIÆ\r\nquaedam, ad recipendum animam intellectivam'
    q = query(['materiae', 'ad recipiendum animam intellectivam'], [{'min': 1, 'max': 40}])
    hit = search(raw, q, max_edits=1)['hits'][0]
    assert hit['mode'] == 'bounded-gap' and hit['edits'] == 1
    assert hit['text'] == raw[hit['start']:hit['end']]
    assert [s['text'] for s in hit['segments']] == ['MATERIÆ', 'ad recipendum animam intellectivam']
    assert hit['gap_normalized_characters'] == [8]
    assert hit['gap_bounds'] == [{'min': 1, 'max': 40}]
    assert all(raw[s['start']:s['end']] == s['text'] for s in hit['segments'])


def test_partial_words_and_alternatives_remain_explicit():
    q = query(['mater*', 'anim*'], [{'min': 1, 'max': 2}])
    q['anchors'][0]['variants'].append({'text': 'forma prima', 'basis': 'another reading'})
    hits = search('materia anima forma prima', q)['hits']
    assert [h['variant'] for h in hits] == [0, 1]
    assert hits[0]['segments'][0]['mode'] == 'partial-word'
    q['anchors'][0].update(common=True, reason='shared formula')
    assert not search('materia anima forma prima', q)['passages']


@pytest.mark.parametrize('parts,gaps', [
    (['aaa'], []), (['aaa','bbb'], []), (['aaa','bbb'], [{'min': -1,'max': 4}]),
    (['aaa','bbb'], [{'min': 4,'max': 3}]), (['aaa','bbb'], [{'min': 0,'max': True}]),
    (['aaa','bbb'], [{'min': 0,'max': 1.5}]), (['aaa','bbb'], [{'max': 5}]),
    (['aaa', '*'], [{'min': 0,'max': 5}]), (['aaa', None], [{'min': 0,'max': 5}]),
])
def test_invalid_gaps_fail_before_search(parts, gaps):
    with pytest.raises(ValueError):
        search('aaa bbb', query(parts, gaps))


def test_text_and_parts_cannot_be_mixed():
    with pytest.raises(ValueError):
        search('aaa bbb', query(['aaa','bbb'], [{'min': 0,'max': 5}], text='aaa'))


def test_dynamic_paths_match_exhaustive_reference():
    rng = random.Random(28)
    for _ in range(80):
        raw = ' '.join(rng.choice(['aaa','bbb','ccc','xxxx']) for _ in range(12))
        index = latin.TextIndex(raw)
        parts = ['aaa','bbb','ccc']
        gaps = [{'min': rng.randrange(3), 'max': rng.randrange(3,18)} for _ in range(2)]
        expected = set()
        for chain in itertools.product(*(list(index.find(p,0)) for p in parts)):
            if all(g['min'] <= b[0]-a[1] <= g['max'] for a,b,g in zip(chain,chain[1:],gaps)):
                expected.add((chain[0][0],chain[-1][1]))
        actual = search(raw, query(parts,gaps))['hits']
        assert {(h['start'],h['end']) for h in actual} == expected
