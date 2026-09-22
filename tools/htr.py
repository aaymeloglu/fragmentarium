#!/usr/bin/env python3
"""Run pinned Kraken/CATMuS on a neutral packet; preserve raw PAGE XML and text.

Inference needs the separate htr environment. Other commands use the standard library.
"""
import argparse
from datetime import datetime, timezone
import html
from importlib import metadata, resources
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.request
from xml.etree import ElementTree as ET

import readings

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'htr' / 'models.json'


def model_lock():
    return json.loads(LOCK.read_text())


def verified(path, expected):
    readings.require(readings.sha(path.read_bytes()) == expected, f'File checksum mismatch: {path.name}')
    return path


def download(directory):
    model = model_lock()['recognition']
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / model['filename']
    if path.exists():
        return verified(path, model['sha256'])
    # Never leave a partial download at the final model name.
    with urllib.request.urlopen(model['url'], timeout=120) as response:
        data = response.read()
    readings.require(readings.sha(data) == model['sha256'], 'Downloaded model checksum mismatch')
    with path.open('xb') as f:
        f.write(data)
    return path


def lines(page):
    """Use only line-level Unicode; word/glyph descendants would duplicate the text."""
    doc = ET.fromstring(page['page_xml'])
    for line in doc.findall('.//{*}TextLine'):
        readings.require(line.find('./{*}Coords') is not None, 'HTR line has no coordinates')
    return [{'id': f"{page['name']}:L{i:03d}", 'xml_id': line.get('id'),
             'text': line.findtext('./{*}TextEquiv/{*}Unicode') or '',
             'polygon': line.find('./{*}Coords').get('points')}
            for i, line in enumerate(doc.findall('.//{*}TextLine'), 1)]


def transcript(pages):
    return ''.join(f"{line['id']}: {line['text']}\n" for p in pages for line in lines(p))


def validate_run(run):
    readings.require(run['format'] == 'kraken-catmus-v1' and run['pages'], 'Invalid HTR run')
    readings.require(datetime.fromisoformat(run['created_at']).utcoffset() is not None, 'HTR run needs a UTC offset')
    readings.require(all(run['engine'].get(k) for k in ('python', 'platform', 'machine', 'packages')),
                     'Missing runtime provenance')
    readings.require(run['settings'] == {'device': 'cpu', 'threads': 1, 'segmentation': 'baseline',
                                        'subline_segmentation': False, 'preprocessing': 'none'},
                     'Unexpected HTR settings for kraken-catmus-v1')
    readings.require(run['engine']['kraken'] == run['models']['kraken_version'], 'Kraken version mismatch')
    for model in ('recognition', 'segmentation'):
        readings.require(readings.DIGEST.fullmatch(run['models'][model]['sha256']), 'Missing model digest')
    names = []
    for page in run['pages']:
        name = page['name']
        readings.require(re.fullmatch(r'image-\d{3}\.(jpg|jpeg|png|tif|tiff)', name), 'Invalid HTR image name')
        readings.require(readings.DIGEST.fullmatch(page['image_sha256']), 'Missing image digest')
        readings.require(readings.sha(page['page_xml'].encode('utf-8')) == page['xml_sha256'], 'Raw XML changed')
        node = ET.fromstring(page['page_xml']).find('./{*}Page')
        readings.require(node is not None and node.get('imageFilename') == name, 'XML/image mismatch')
        readings.require(int(node.get('imageWidth')) > 0 and int(node.get('imageHeight')) > 0, 'Invalid image dimensions')
        lines(page)
        names.append(name)
    readings.require(len(names) == len(set(names)), 'Duplicate HTR images')
    readings.require(run['text'] == transcript(run['pages']), 'HTR text differs from raw XML')


def render_review(run, output):
    sections = []
    for page in run['pages']:
        node = ET.fromstring(page['page_xml']).find('./{*}Page')
        width, height = int(node.get('imageWidth')), int(node.get('imageHeight'))
        rows, shapes = [], []
        for i, line in enumerate(lines(page), 1):
            # Parse numeric coordinates before including them in SVG.
            points = ' '.join(f'{float(x):g},{float(y):g}' for x,y in (p.split(',') for p in line['polygon'].split()))
            x, y = points.split()[0].split(',')
            shapes.append(f'<polygon points="{points}"><title>{html.escape(line["id"])}</title></polygon>'
                          f'<text x="{x}" y="{y}">{i}</text>')
            rows.append(f'<tr><td>{i}</td><td><pre>{html.escape(line["text"]) or "[empty recognition]"}</pre></td></tr>')
        sections.append(f'<h2>{html.escape(page["name"])}</h2><div class="pair">'
                        f'<svg viewBox="0 0 {width} {height}"><image href="images/{page["name"]}" '
                        f'width="{width}" height="{height}"/>{"".join(shapes)}</svg>'
                        f'<table>{"".join(rows)}</table></div>')
    output.write_text('<!doctype html><meta charset="utf-8"><title>Raw HTR review</title>'
                     '<style>body{font-family:system-ui;margin:2rem}.pair{display:grid;grid-template-columns:1fr 1fr;gap:2rem}'
                     'svg{width:100%}polygon{fill:none;stroke:#e53535;stroke-width:2}text{fill:#e53535;font-size:24px}'
                     'td{vertical-align:top;padding:.25rem}pre{white-space:pre-wrap;margin:0}</style>'
                     '<h1>Raw HTR review</h1><p>Check line boundaries, order, omissions, and marginalia against the image. '
                     'Numbers identify detections, not verified physical lines. Recognition is unverified.</p>'
                     + ''.join(f'<p>{html.escape(w)}</p>' for w in run['warnings']) + ''.join(sections))


def run_packet(packet, output, model_dir):
    inputs = readings.read_packet(packet)
    lock = model_lock()
    version = metadata.version('kraken')
    readings.require(version == lock['kraken_version'], 'Use the pinned htr environment; see HTR.md')
    model = verified(model_dir / lock['recognition']['filename'], lock['recognition']['sha256'])
    segmenter = verified(Path(str(resources.files('kraken').joinpath('blla.mlmodel'))), lock['segmentation']['sha256'])
    executable = Path(sys.executable).parent / 'kraken'
    output.mkdir(parents=True, exist_ok=False)
    (output / 'images').mkdir()
    (output / 'raw').mkdir()
    pages, warnings = [], []
    # Copy only verified pixel inputs. No catalogue, prompt, or other reader's text reaches Kraken.
    for image in inputs['images']:
        shutil.copyfile(packet / image['name'], output / 'images' / image['name'])
        verified(output / 'images' / image['name'], image['sha256'])
    for image in inputs['images']:
        name = image['name']
        xml = output / 'raw' / f'{name}.xml'
        command = [str(executable), '--raise-on-error', '--no-subline-segmentation', '--threads', '1',
                   '--device', 'cpu', '-x', '-i', name, str(xml), 'segment', '-bl', '--model', str(segmenter),
                   'ocr', '-m', str(model)]
        result = subprocess.run(command, cwd=output / 'images', capture_output=True, text=True)
        (output / 'raw' / f'{name}.log').write_text(result.stdout + result.stderr)
        readings.require(result.returncode == 0, f'Kraken failed for {name}; see raw/{name}.log. No complete run saved.')
        raw = readings.text_file(xml)
        page = {'name': name, 'image_sha256': image['sha256'], 'page_xml': raw,
                'xml_sha256': readings.sha(raw.encode('utf-8'))}
        detected = lines(page)
        if not detected:
            warnings.append(f'{name}: ZERO LINES DETECTED. Review input scale/layout; this run cannot be frozen.')
        elif any(not line['text'].strip() for line in detected):
            warnings.append(f'{name}: empty recognized lines; inspect the overlay.')
        pages.append(page)
        print(f'{name}: {len(detected)} detected lines', flush=True)
    run = {'format': 'kraken-catmus-v1', 'created_at': datetime.now(timezone.utc).isoformat(),
           'engine': {'kraken': version, 'python': platform.python_version(),
                      'platform': sys.platform, 'machine': platform.machine(),
                      'packages': {d.metadata['Name']: d.version for d in metadata.distributions()}},
           'models': lock, 'settings': {'device': 'cpu', 'threads': 1, 'segmentation': 'baseline',
                                      'subline_segmentation': False, 'preprocessing': 'none'},
           'pages': pages, 'warnings': warnings, 'text': transcript(pages)}
    validate_run(run)
    (output / 'run.json').write_bytes(readings.encoded(run))
    (output / 'transcript.txt').write_bytes(run['text'].encode('utf-8'))
    render_review(run, output / 'review.html')
    return run


def derive_layers(run_path, expansions_path, output):
    """Optional proposed expansions; never modify raw recognition or silently fill gaps."""
    run = json.loads(run_path.read_text())
    validate_run(run)
    expansions = json.loads(expansions_path.read_text())
    raw = {line['id']: line['text'] for page in run['pages'] for line in lines(page)}
    readings.require(isinstance(expansions, dict) and set(expansions) <= set(raw), 'Unknown expansion line IDs')
    derived = []
    for line_id, text in raw.items():
        proposed = expansions.get(line_id)
        if proposed is not None:
            readings.require(isinstance(proposed.get('text'), str) and proposed['text'].strip()
                             and isinstance(proposed.get('uncertain'), bool)
                             and proposed.get('basis', '').strip(), 'Expansion needs text, uncertain, and basis')
        # Only Unicode composition and whitespace. Latin matching rules belong to retrieval (#3).
        searchable = proposed['text'] if proposed else text
        derived.append({'line_id': line_id, 'raw': text, 'proposed_expansion': proposed,
                        'search_text': ' '.join(unicodedata.normalize('NFC', searchable).split()),
                        'search_basis': 'proposed_expansion' if proposed else 'raw'})
    with output.open('xb') as f:
        f.write(readings.encoded({'raw_run_sha256': readings.sha(run_path.read_bytes()),
                                 'status': 'unverified-derived-layers', 'lines': derived}))
    return output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('download-model')
    a.add_argument('directory', type=Path)
    a = sub.add_parser('run')
    a.add_argument('--packet', type=Path, required=True)
    a.add_argument('--output', type=Path, required=True)
    a.add_argument('--model-dir', type=Path, required=True)
    a = sub.add_parser('layers')
    a.add_argument('--run', type=Path, required=True)
    a.add_argument('--expansions', type=Path, required=True)
    a.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    try:
        if args.command == 'download-model':
            print(download(args.directory.resolve()))
        elif args.command == 'layers':
            print(derive_layers(args.run, args.expansions, args.output))
        else:
            run = run_packet(args.packet.resolve(), args.output.resolve(), args.model_dir.resolve())
            print(args.output / 'review.html')
            if any(not lines(page) for page in run['pages']):
                p.exit(2, 'Incomplete segmentation. Diagnostics saved; do not treat this as a reading.\n')
    except (ValueError, KeyError, TypeError, OSError, ET.ParseError, metadata.PackageNotFoundError) as e:
        p.exit(1, f'{e}\n')


if __name__ == '__main__':
    main()
