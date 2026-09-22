#!/usr/bin/env python3
"""Preserve first image readings and separately labelled source-assisted revisions.

See FIRST_READINGS.md for the isolated-reader workflow. Standard library only.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r"[a-z0-9][a-z0-9_-]{0,79}")
FRAGMENT = re.compile(r"F-[a-z0-9]{4}")
DIGEST = re.compile(r"[0-9a-f]{64}")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode('utf-8') + b'\n'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text_file(path):
    # read_text() translates CRLF; preserve the original response exactly instead.
    value = Path(path).read_bytes().decode('utf-8')
    require(value.strip(), f"Empty text: {path}")
    return value


def packet(output, images):
    """Copy images under neutral names; never include source filenames or catalogue data."""
    images = [Path(p) for p in images]
    require(images, 'At least one image is required')
    for p in images:
        require(p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.tif', '.tiff'},
                f'Expected a local image: {p}')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    items = []
    for i, p in enumerate(images, 1):
        name = f'image-{i:03d}{p.suffix.lower()}'
        shutil.copyfile(p, output / name)
        items.append({'name': name, 'sha256': sha((output / name).read_bytes())})
    prompt = (ROOT / 'prompts' / 'first-reading.md').read_bytes()
    (output / 'PROMPT.md').write_bytes(prompt)
    (output / 'packet.json').write_bytes(encoded({
        'images': items, 'prompt_sha256': sha(prompt),
    }))
    return output


def read_packet(directory):
    directory = Path(directory)
    p = json.loads((directory / 'packet.json').read_text())
    require(isinstance(p.get('images'), list) and p['images'], 'Packet has no images')
    names = []
    for image in p['images']:
        name = image['name']
        require(re.fullmatch(r'image-\d{3}\.(jpg|jpeg|png|tif|tiff)', name), 'Invalid packet image name')
        require(sha((directory / name).read_bytes()) == image['sha256'], f'Image changed: {name}')
        names.append(name)
    require(len(names) == len(set(names)), 'Duplicate packet image names')
    prompt = text_file(directory / 'PROMPT.md')
    require(sha(prompt.encode('utf-8')) == p['prompt_sha256'], 'Packet prompt changed')
    return {'images': p['images'], 'prompt': prompt}


def save(root, fragment, name, record):
    require(FRAGMENT.fullmatch(fragment), 'Invalid fragment ID')
    require(SLUG.fullmatch(name), 'Invalid reading name')
    require((root / 'fragments' / fragment / 'README.md').is_file(), 'Unknown fragment')
    record.update(schema_version=1, fragment=fragment, id=name,
                  captured_at=datetime.now(timezone.utc).isoformat())
    record['text_sha256'] = sha(record['text'].encode('utf-8'))
    dest = root / 'fragments' / fragment / 'readings' / f'{name}.json'
    dest.parent.mkdir(exist_ok=True)
    # Exclusive creation prevents accidentally replacing an earlier reading.
    with dest.open('xb') as f:
        f.write(encoded(record))
    return dest


def freeze(root, args):
    require(args.attest_isolated, 'First reading requires --attest-isolated; see FIRST_READINGS.md')
    require(args.reader.strip() and args.session.strip(), 'Reader and fresh session reference are required')
    p = read_packet(args.packet)
    require(len(args.image_source) == len(p['images']) and all(s.strip() for s in args.image_source),
            'Provide one --image-source citation per packet image, in packet order')
    for image, source in zip(p['images'], args.image_source):
        image['source'] = source
    return save(root, args.fragment, args.name, {
        'kind': 'image-only', 'reader': args.reader, 'session': args.session,
        'isolation_attested': True, 'packet': p, 'text': text_file(args.text),
    })


def revise(root, args):
    require(FRAGMENT.fullmatch(args.fragment), 'Invalid fragment ID')
    require(SLUG.fullmatch(args.first), 'Invalid first-reading name')
    base = root / 'fragments' / args.fragment / 'readings' / f'{args.first}.json'
    first = json.loads(base.read_text())
    validate(first, base)
    require(first['kind'] == 'image-only', 'Revisions must reference the first image-only reading')
    require(args.reader.strip() and args.reason.strip(), 'Reader and reason are required')
    require(args.source and all(s.strip() for s in args.source), 'Source citations are required')
    return save(root, args.fragment, args.name, {
        'kind': 'source-assisted', 'reader': args.reader,
        'first_reading': args.first, 'first_sha256': sha(base.read_bytes()),
        'sources': args.source, 'reason': args.reason, 'text': text_file(args.text),
    })


def validate(r, path):
    require(r['schema_version'] == 1, f'{path}: unsupported schema')
    require(FRAGMENT.fullmatch(r['fragment']) and SLUG.fullmatch(r['id']), f'{path}: invalid ID')
    require(path.stem == r['id'] and path.parent.parent.name == r['fragment'], f'{path}: ID/path mismatch')
    require(r['reader'].strip() and r['text'].strip(), f'{path}: empty reader/text')
    require(datetime.fromisoformat(r['captured_at']).utcoffset() is not None, f'{path}: timezone missing')
    require(sha(r['text'].encode('utf-8')) == r['text_sha256'], f'{path}: text checksum mismatch')
    if r['kind'] == 'image-only':
        require(r['isolation_attested'] is True and r['session'].strip(), f'{path}: missing isolation attestation')
        p = r['packet']
        require(p['prompt'].strip() and p['images'], f'{path}: missing reader input')
        names = []
        for image in p['images']:
            require(re.fullmatch(r'image-\d{3}\.(jpg|jpeg|png|tif|tiff)', image['name']), f'{path}: invalid image name')
            require(DIGEST.fullmatch(image['sha256']), f'{path}: invalid image digest')
            require(image['source'].strip(), f'{path}: missing image source citation')
            names.append(image['name'])
        require(len(names) == len(set(names)), f'{path}: duplicate images')
    elif r['kind'] == 'source-assisted':
        require(SLUG.fullmatch(r['first_reading']), f'{path}: invalid first-reading reference')
        require(DIGEST.fullmatch(r['first_sha256']), f'{path}: invalid first-reading digest')
        require(r['reason'].strip() and isinstance(r['sources'], list) and r['sources']
                and all(s.strip() for s in r['sources']), f'{path}: missing revision reason/sources')
    else:
        raise ValueError(f'{path}: unknown reading kind')


def check(root, base=None):
    count = 0
    for path in sorted((root / 'fragments').glob('*/readings/*')):
        require(path.is_file() and path.suffix == '.json', f'{path}: expected a reading JSON file')
        require((path.parent.parent / 'README.md').is_file(), f'{path}: unknown fragment')
        r = json.loads(path.read_text())
        validate(r, path)
        if r['kind'] == 'source-assisted':
            first_path = path.parent / f"{r['first_reading']}.json"
            first = json.loads(first_path.read_text())
            require(first['kind'] == 'image-only', f'{path}: base is not image-only')
            require(sha(first_path.read_bytes()) == r['first_sha256'], f'{path}: first reading changed')
            require(datetime.fromisoformat(r['captured_at']) >= datetime.fromisoformat(first['captured_at']),
                    f'{path}: revision predates first reading')
        count += 1
    if base:
        # Compare bytes with the base commit, so rewriting both text and checksum fails too.
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', '-z', base, '--', 'fragments'], cwd=root)
        for raw in paths.split(b'\0'):
            name = raw.decode('utf-8')
            if not re.fullmatch(r'fragments/F-[a-z0-9]{4}/readings/[^/]+\.json', name):
                continue
            original = subprocess.check_output(['git', 'show', f'{base}:{name}'], cwd=root)
            dest = root / name
            require(dest.is_file() and dest.read_bytes() == original, f'Preserved reading modified or deleted: {name}')
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('packet', help='Create an isolated directory with neutral image names and a reading prompt')
    p.add_argument('output', type=Path)
    p.add_argument('images', nargs='+', type=Path)
    p = sub.add_parser('freeze', help='Save a first reading before revealing sources')
    p.add_argument('fragment')
    p.add_argument('name')
    p.add_argument('--packet', required=True, type=Path)
    p.add_argument('--text', required=True, type=Path)
    p.add_argument('--reader', required=True, help='Model/version or human reader')
    p.add_argument('--session', required=True, help='Fresh session reference; no local paths or private details')
    p.add_argument('--attest-isolated', action='store_true')
    p.add_argument('--image-source', action='append', required=True,
                   help='Image URL or canvas/region citation, one per image in packet order; kept from reader')
    p = sub.add_parser('revise', help='Save a separately labelled source-assisted reading')
    p.add_argument('fragment')
    p.add_argument('name')
    p.add_argument('--first', required=True)
    p.add_argument('--text', required=True, type=Path)
    p.add_argument('--reader', required=True)
    p.add_argument('--source', action='append', required=True, help='Edition/report citation; repeat for each source')
    p.add_argument('--reason', required=True)
    p = sub.add_parser('check', help='Validate records, optionally enforcing preservation against a Git base')
    p.add_argument('--base', help='Existing Git commit/ref to compare against')
    args = parser.parse_args()
    try:
        if args.command == 'packet':
            print(packet(args.output, args.images))
        elif args.command == 'freeze':
            print(freeze(ROOT, args))
        elif args.command == 'revise':
            print(revise(ROOT, args))
        else:
            print(f'{check(ROOT, args.base)} preserved readings checked')
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as e:
        parser.exit(1, f'{e}\n')


if __name__ == '__main__':
    main()
