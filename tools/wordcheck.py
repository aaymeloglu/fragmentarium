#!/usr/bin/env python3
"""Blind word check for archival documents: neutral crop sets for fresh readers, then pair their answers.

    uv run python tools/wordcheck.py make EVIDENCE/F-aaaa/wordcheck EVIDENCE/F-bbbb/wordcheck \
        --out /tmp/wc --key WORK/wordcheck.key.tsv [--sets 2] [--seed 4]
    uv run python tools/wordcheck.py pair WORK/wordcheck.key.tsv /tmp/wc/answers-a.txt /tmp/wc/answers-b.txt

A document's regest rests on single words (a year in words, a day, a surname, a place), and a
reader who has the transcription open tends to confirm it. `make` takes the crops the research
session cut (document-brief.md, "Crops for the word check"), from one or several documents, and
copies them into sets `a`, `b`, ... under `--out`, each in its own shuffled order and renamed
`crop-NN.jpg`, so a reader sees neither the record, the file name nor which crops belong together.
Each set gets `PROMPT.md`, the reader's instructions. Give one set to each fresh reader (a separate
session or subagent with no other context), who writes `answers-<set>.txt` beside it.

The key (crop -> original file) goes to `--key`, which must be outside `--out`: keep it from the
readers. Mixing two or more documents in one run makes each crop harder to place.

`pair` prints, for each original crop, every reader's answer for it, so the coordinator can set
them beside the research reading and reread every disagreement on the image. A disagreement is
not settled by majority: readers misread too, so the image decides, and what stays unclear is
marked uncertain. Standard library only.
"""
import argparse
import random
import re
import shutil
import sys
from pathlib import Path

PROMPT = """You are a fresh reader of handwriting. You have no other task.

This directory holds crop-01.jpg ... crop-{n:02d}.jpg: small crops of documents in a historical
script. Open nothing except these image files (you may make enlarged or contrast-stretched copies
in your own scratch directory). Do not use the web or any search tool, and do not list or read any
other directory.

For each crop, transcribe every word you can see, letter by letter, line by line, without guessing
at sense: mark uncertain letters with ?, lost letters with [..], and give alternative readings
where letters are ambiguous. Pay special attention to names of people and places, numbers and
number words, saints' names and month or day words. Do not supply words from what would make sense.

Write the result as plain text to answers-{name}.txt in this directory, one section per crop,
headed "=== crop-NN.jpg ===". Say at the top if anything other than these images told you what the
documents are.
"""
IMAGE = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.webp'}
SECTION = re.compile(r'^=== (crop-\d+\.\w+) ===[ \t]*$', re.M)


def crops_of(paths):
    """Image files named directly or found in the directories given, in a stable order."""
    out = []
    for p in map(Path, paths):
        if p.is_dir():
            out += sorted(f for f in p.iterdir() if f.suffix.lower() in IMAGE)
        elif p.suffix.lower() in IMAGE:
            out.append(p)
        else:
            raise SystemExit(f'not an image or directory: {p}')
    if len(set(map(str, out))) != len(out):
        raise SystemExit('the same crop is listed twice')
    return out


def make(crops, out, key, sets=2, seed=4):
    out, key = Path(out), Path(key)
    if key.resolve().is_relative_to(out.resolve()):
        raise SystemExit('--key must be outside --out, where the readers cannot see it')
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f'{out} is not empty')
    names = [chr(ord('a') + i) for i in range(sets)]
    rows = []
    for i, name in enumerate(names):
        order = crops[:]
        random.Random(seed + 1000 * i).shuffle(order)
        folder = out / name
        folder.mkdir(parents=True)
        for n, src in enumerate(order, 1):
            dst = f'crop-{n:02d}{src.suffix.lower()}'
            shutil.copyfile(src, folder / dst)
            rows.append((f'{name}/{dst}', str(src)))
        (folder / 'PROMPT.md').write_text(PROMPT.format(n=len(order), name=name))
    key.parent.mkdir(parents=True, exist_ok=True)
    key.write_text(''.join(f'{a}\t{b}\n' for a, b in rows))
    return names


def sections(text):
    """crop file name -> that crop's answer text."""
    parts = SECTION.split(text)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def pair(key, answers):
    """[(original crop, [(set, answer or None), ...]), ...] in the order of the originals."""
    rows = [line.split('\t') for line in Path(key).read_text().splitlines() if line.strip()]
    by_set = {}
    for path in map(Path, answers):
        m = re.fullmatch(r'answers-(\w+)\.txt', path.name)
        if not m:
            raise SystemExit(f'answer files are named answers-<set>.txt: {path}')
        by_set[m.group(1)] = sections(path.read_text())
    grouped = {}
    for crop, original in rows:
        name, file = crop.split('/', 1)
        if name in by_set:
            grouped.setdefault(original, []).append((name, by_set[name].get(file)))
    return sorted(grouped.items())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    m = sub.add_parser('make', help='neutral shuffled crop sets for fresh readers')
    m.add_argument('crops', nargs='+', help='crop images, or directories of them')
    m.add_argument('--out', required=True, help='new directory for the reader sets')
    m.add_argument('--key', required=True, help='where to write the key; outside --out')
    m.add_argument('--sets', type=int, default=2, help='number of readers (default 2)')
    m.add_argument('--seed', type=int, default=4)
    p = sub.add_parser('pair', help="each original crop with every reader's answer")
    p.add_argument('key')
    p.add_argument('answers', nargs='+', help='answers-<set>.txt files')
    args = parser.parse_args(argv)
    if args.command == 'make':
        crops = crops_of(args.crops)
        names = make(crops, args.out, args.key, args.sets, args.seed)
        print(f'{len(crops)} crops in sets {", ".join(names)} under {args.out}; key in {args.key}')
        print('Give each set to its own fresh reader with only: "Read PROMPT.md in <set dir> and follow it."')
    else:
        for original, answers in pair(args.key, args.answers):
            print(f'##### {original}')
            for name, text in answers:
                print(f'-- {name.upper()}: ' + (text if text is not None else '[no answer for this crop]'))
            print()


if __name__ == '__main__':
    sys.exit(main())
