"""Image packet reuse must never misstate source bytes or resolution."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import acquire_batch


def fake_library(monkeypatch):
    calls = []
    manifest = {'sequences': [{'canvases': [{'images': [{'resource': {
        '@id': 'https://example.org/image/full/full/0/default.jpg',
        'service': {'@id': 'https://example.org/image'},
    }}]}]}]}

    def fetch(url, path):
        calls.append(url)
        if path.exists():
            return path.read_bytes()
        if url.endswith('manifest.json'):
            data = json.dumps(manifest).encode()
        elif url.endswith('info.json'):
            data = json.dumps({'width': 7000, 'height': 9000}).encode()
        else:
            # Deterministic bytes stand in for two differently sized JPEGs.
            data = b'\xff\xd8' + url.encode()
        path.write_bytes(data)
        return data

    monkeypatch.setattr(acquire_batch, 'fetch', fetch)
    return calls


def test_native_request_does_not_reuse_cached_overview(tmp_path, monkeypatch):
    calls = fake_library(monkeypatch)
    dest = tmp_path / 'images'
    acquire_batch.acquire('F-test', dest, tmp_path / 'overview', 1, max_width=5000)
    result = acquire_batch.acquire('F-test', dest, tmp_path / 'native', 1)
    assert result['sources'][0]['requested_width'] == 7000
    packet = tmp_path / 'native/packet-01/image-001.jpg'
    assert b'/full/7000,/' in packet.read_bytes()
    assert any('/full/7000,/' in call for call in calls)


def test_changed_sources_cannot_relabel_existing_packet(tmp_path, monkeypatch):
    fake_library(monkeypatch)
    dest, packets = tmp_path / 'images', tmp_path / 'packets'
    acquire_batch.acquire('F-test', dest, packets, 1, max_width=5000)
    original = (dest / 'F-test/acquisition.json').read_bytes()
    with pytest.raises(ValueError, match='different images'):
        acquire_batch.acquire('F-test', dest, packets, 1)
    assert (dest / 'F-test/acquisition.json').read_bytes() == original
    assert b'/full/5000,/' in (packets / 'packet-01/image-001.jpg').read_bytes()


def test_canvas_with_another_canvas_image_is_an_error_not_a_download(tmp_path, monkeypatch):
    resource = {'@id': 'https://example.org/one/full/full/0/default.jpg', 'service': {'@id': 'https://example.org/one'}}
    manifest = {'sequences': [{'canvases': [
        {'label': 'recto', 'width': 7000, 'height': 9000, 'images': [{'resource': resource}]},
        {'label': 'verso', 'width': 7000, 'height': 9000, 'images': [{'resource': resource}]}]}]}

    def fetch(url, path):
        if url.endswith('manifest.json'):
            data = json.dumps(manifest).encode()
        elif url.endswith('info.json'):
            data = json.dumps({'width': 7000, 'height': 9000}).encode()
        else:
            data = b'\xff\xd8' + url.encode()
        path.write_bytes(data)
        return data

    monkeypatch.setattr(acquire_batch, 'fetch', fetch)
    result = acquire_batch.acquire('F-test', tmp_path / 'images', tmp_path / 'packets', 1)
    assert [s['canvas'] for s in result['sources']] == [0]
    assert result['errors'][0]['canvas'] == 1 and 'same image as canvas 0' in result['errors'][0]['error']
    assert not (tmp_path / 'images/F-test/canvas-1-w7000.jpg').exists()
