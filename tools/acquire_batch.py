#!/usr/bin/env python3
"""Cache selected Fragmentarium manifests and neutral image packets for a research batch.

Downloads at most the requested number of canvases per fragment, sequentially.
Source metadata stays with the coordinator, outside the neutral packets.
"""
import argparse
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


def acquire(fid, destination, packet_root, number, count=2):
    folder = destination / fid
    folder.mkdir(parents=True, exist_ok=True)
    url = f'https://fragmentarium.ms/metadata/iiif/{fid}/manifest.json'
    manifest = json.loads(fetch(url, folder / 'manifest.json'))
    sources, images, errors = [], [], []
    for i, canvas in enumerate(manifest['sequences'][0]['canvases'][:count]):
        try:
            resource = canvas['images'][0]['resource']
            service = resource.get('service')
            base = service.get('@id') if isinstance(service, dict) else None
            base = base or resource['@id'].split('/full/')[0]
            info = json.loads(fetch(base + '/info.json', folder / f'canvas-{i}-info.json'))
            width, height = info['width'], info['height']
            ext = 'native.jpg' if 'gallica' in base else 'default.jpg'
            target_width = min(width, 5000)
            image_url = f'{base}/full/{target_width},/0/{ext}'
            path = folder / f'canvas-{i}.jpg'
            content = fetch(image_url, path)
            if not content.startswith(b'\xff\xd8'):
                path.unlink()
                raise ValueError('Not a JPEG image')
            sources.append({'canvas': i, 'label': canvas.get('label'), 'source': image_url,
                            'native_width': width, 'native_height': height, 'requested_width': target_width})
            images.append(path)
        except Exception as error:
            errors.append({'canvas': i, 'error': str(error)})
    output = {'fragment': fid, 'manifest': url, 'sources': sources, 'errors': errors}
    if images:
        packet = packet_root / f'packet-{number:02d}'
        if not packet.exists():
            readings.packet(packet, images)
        output['packet'] = str(packet)
    (folder / 'acquisition.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n')
    print(fid, f'{len(images)} images', f'{len(errors)} errors', flush=True)
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--packets',type=Path,required=True)
    args=parser.parse_args()
    args.packets.mkdir(parents=True,exist_ok=True)
    for i,fid in enumerate(json.loads(args.selection.read_text()),1):
        try: acquire(fid,args.output,args.packets,i)
        except Exception as error: print(fid,'FAILED',str(error),flush=True)


if __name__=='__main__': main()
