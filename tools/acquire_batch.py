#!/usr/bin/env python3
"""Cache selected Fragmentarium manifests and neutral image packets for a research batch.

Downloads at most the requested number of canvases per fragment, sequentially.
Images use library-native width unless --max-width requests smaller overviews.
Source metadata stays with the coordinator, outside the neutral packets.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import urllib.request
import readings
import iiif


def fetch(url, path):
    if path.exists():
        return path.read_bytes()
    response = urllib.request.urlopen(urllib.request.Request(url, headers=iiif.UA), timeout=60)
    data = response.read()
    path.write_bytes(data)
    time.sleep(1)
    return data


def acquire(fid, destination, packet_root, number, count=2, max_width=0):
    folder = destination / fid
    folder.mkdir(parents=True, exist_ok=True)
    url = f'https://fragmentarium.ms/metadata/iiif/{fid}/manifest.json'
    manifest = json.loads(fetch(url, folder / 'manifest.json'))
    sources, images, errors = [], [], []
    canvases = manifest['sequences'][0]['canvases']
    resolved = []
    for canvas in canvases:
        resource = canvas['images'][0]['resource']
        service = resource.get('service')
        base = service.get('@id') if isinstance(service, dict) else None
        resolved.append(iiif.image_base(base or resource['@id'].split('/full/')[0]))
    # A manifest can give several canvases one image; correct what can be verified, refuse the rest.
    bases, notes = iiif.resolve_duplicates(
        [base for base, _, _ in resolved], [(c.get('width'), c.get('height')) for c in canvases])
    for i, canvas in enumerate(canvases[:count]):
        try:
            base, ext = bases[i], resolved[i][1]
            if (notes[i] or '').startswith('FAULT'):
                raise ValueError(notes[i])
            info = json.loads(fetch(base + '/info.json', folder / f'canvas-{i}-info.json'))
            width, height = info['width'], info['height']
            target_width = min(width, max_width) if max_width else width
            image_url = f'{base}/full/{target_width},/0/{ext}'
            # Include requested width so a cached overview cannot be relabelled
            # as a native-resolution image on a later run.
            path = folder / f'canvas-{i}-w{target_width}.jpg'
            content = fetch(image_url, path)
            if not content.startswith(b'\xff\xd8'):
                path.unlink()
                raise ValueError('Not a JPEG image')
            sources.append({'canvas': i, 'label': canvas.get('label'), 'source': image_url,
                            'native_width': width, 'native_height': height, 'requested_width': target_width,
                            **({'note': notes[i]} if notes[i] else {})})
            images.append(path)
        except Exception as error:
            errors.append({'canvas': i, 'error': str(error)})
    output = {'fragment': fid, 'manifest': url, 'sources': sources, 'errors': errors}
    if images:
        packet = packet_root / f'packet-{number:02d}'
        if not packet.exists():
            readings.packet(packet, images)
        else:
            existing = readings.read_packet(packet)
            hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in images]
            if hashes != [item['sha256'] for item in existing['images']]:
                raise ValueError('Existing packet has different images; use a fresh packet root')
        output['packet'] = str(packet)
    (folder / 'acquisition.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n')
    print(fid, f'{len(images)} images', f'{len(errors)} errors', flush=True)
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--packets',type=Path,required=True)
    parser.add_argument('--canvases',type=int,default=2)
    parser.add_argument('--max-width',type=int,default=0,
                        help='Overview width cap; 0 (default) preserves native pixels')
    args=parser.parse_args()
    if args.canvases < 1 or args.max_width < 0:
        parser.error('--canvases must be positive and --max-width nonnegative')
    args.packets.mkdir(parents=True,exist_ok=True)
    failed = False
    for i,fid in enumerate(json.loads(args.selection.read_text()),1):
        try:
            result = acquire(fid,args.output,args.packets,i,args.canvases,args.max_width)
            failed |= bool(result['errors']) or not result['sources']
        except Exception as error:
            failed = True
            print(fid,'FAILED',str(error),flush=True)
    if failed:
        raise SystemExit(1)


if __name__=='__main__': main()
