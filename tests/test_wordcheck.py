from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import wordcheck


def _crops(tmp_path):
    for doc, names in (('F-aaaa', ['wc1_year.jpg', 'wc2_name.jpg']), ('F-bbbb', ['wc1_place.jpg'])):
        d = tmp_path / 'evidence' / doc / 'wordcheck'
        d.mkdir(parents=True)
        for n in names:
            (d / n).write_bytes(f'{doc}/{n}'.encode())
        (d / 'notes.txt').write_text('not an image')
    return [tmp_path / 'evidence' / 'F-aaaa' / 'wordcheck', tmp_path / 'evidence' / 'F-bbbb' / 'wordcheck']


def test_sets_are_neutral_shuffled_and_keyed_outside_the_readers_view(tmp_path):
    crops = wordcheck.crops_of(_crops(tmp_path))
    assert len(crops) == 3  # the text file is not a crop
    out, key = tmp_path / 'sets', tmp_path / 'work' / 'key.tsv'
    assert wordcheck.make(crops, out, key, sets=2) == ['a', 'b']
    for name in 'ab':
        files = sorted(p.name for p in (out / name).iterdir())
        assert files == ['PROMPT.md', 'crop-01.jpg', 'crop-02.jpg', 'crop-03.jpg']
        prompt = (out / name / 'PROMPT.md').read_text()
        assert 'F-aaaa' not in prompt and f'answers-{name}.txt' in prompt
    rows = dict(line.split('\t') for line in key.read_text().splitlines())
    assert len(rows) == 6
    # every copy is the crop the key says it is
    for crop, original in rows.items():
        assert (out / crop).read_bytes() == Path(original).read_bytes()
    with pytest.raises(SystemExit):
        wordcheck.make(crops, tmp_path / 'sets2', tmp_path / 'sets2' / 'key.tsv')
    with pytest.raises(SystemExit):
        wordcheck.make(crops, out, tmp_path / 'other.tsv')  # not empty


def test_pair_groups_each_readers_answer_under_the_original_crop(tmp_path):
    crops = wordcheck.crops_of(_crops(tmp_path))
    out, key = tmp_path / 'sets', tmp_path / 'key.tsv'
    wordcheck.make(crops, out, key)
    rows = [line.split('\t') for line in key.read_text().splitlines()]
    for name in 'ab':
        mine = [(c.split('/')[1], o) for c, o in rows if c.startswith(name + '/')]
        text = 'header line\n' + ''.join(f'=== {c} ===\nreader {name} read {Path(o).name}\n' for c, o in mine[:-1])
        (out / f'answers-{name}.txt').write_text(text)
    paired = dict(wordcheck.pair(key, [out / 'answers-a.txt', out / 'answers-b.txt']))
    assert len(paired) == 3
    for original, answers in paired.items():
        assert [n for n, _ in answers] == ['a', 'b']
        for n, text in answers:
            assert text is None or text == f'reader {n} read {Path(original).name}'
    assert sum(text is None for answers in paired.values() for _, text in answers) == 2
    with pytest.raises(SystemExit):
        wordcheck.pair(key, [out / 'a.txt'])


def test_sections_keep_header_remarks_and_refuse_unparsed_headers():
    text = ('note\n=== crop-01.jpg ===\nfirst\n'
            '=== crop-02.jpg ===   (very faded)\nsecond\n'
            '  ===crop-03.jpg===\nthird\n')
    got = wordcheck.sections(text)
    assert got == {'crop-01.jpg': 'first', 'crop-02.jpg': '(very faded)\nsecond', 'crop-03.jpg': 'third'}
    with pytest.raises(SystemExit):
        wordcheck.sections('=== crop-01.jpg ===\nfirst\n=== crop 02 ===\nsecond\n')
    with pytest.raises(SystemExit):
        wordcheck.sections('=== crop-01.jpg ===\nfirst\n=== crop-01.jpg ===\nagain\n')
