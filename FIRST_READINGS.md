# Image acquisition and first-reading commands

Use this reference when preparing a reading. The evidence requirements and the
fallback when isolation is unavailable are in [CONVENTIONS.md](CONVENTIONS.md).
The isolated reader receives only the packet below, not this repository.

## Acquire the selected images

`tools/iiif.py` resolves the library's image service from the Fragmentarium manifest:

```sh
uv run python tools/iiif.py F-xxxx info
uv run python tools/iiif.py F-xxxx overview /tmp/overview
uv run python tools/iiif.py F-xxxx crop /tmp/crops x,y,w,h --canvas 0 --scale 1
# Or a grid when useful for the layout:
uv run python tools/iiif.py F-xxxx tiles /tmp/crops --canvas 0 --cols 2 --rows 4 --scale 1
```

For a batch, `tools/acquire_batch.py --selection /tmp/selection.json --output
/tmp/source-images --packets /tmp/neutral-packets` accepts a JSON list of fragment
IDs, caches the first two canvases each, and creates numbered neutral packets.
It defaults to native image width; `--canvases N` changes coverage and
`--max-width N` explicitly requests smaller overviews. Keep the source cache
separate from readers. Use a fresh packet root when changing the image inputs.

A reader shown only whole native images sees small script reduced and reports gaps.
`tools/tilepacket.py` turns the cache into packets of one reduced overview per canvas
plus overlapping native tiles of the text area (ten to twenty lines each), with a
rotation for sideways or upside-down leaves, and writes the per-image source citations
that `readings.py freeze` needs. Look at every canvas the record lists before choosing
areas: the first two may show a host volume or a neighbouring leaf, not the fragment.

When the native image is already cached, `tools/localcrop.py` cuts the same
regions locally (it needs Pillow: `uv run --group images python tools/localcrop.py
SRC OUT x0,y0,x1,y1`), can rotate an upside-down wrapper and stretch contrast,
and with `--strips N --columns M` cuts a whole face into overlapping reading
bands. It prints each output's native box; cite that box, not the enlarged file.

Use native pixels for recognition (`--scale 1`); magnification adds no evidence.
Record the public image URL or manifest, canvas, region, and any transform. Check
that the resulting crop contains the intended text. Common acquisition problems:

| Symptom | Practical next step |
|---|---|
| Several canvases show the same picture | The manifest points them at one image. `iiif.py` and `acquire_batch.py` correct a canvas when the image at its expected number has the size the manifest gives, and say so (`iiif.py F-xxxx info`); otherwise they mark the canvas as a fault and refuse to fetch it. Do not read a faulted canvas as the leaf its label names. |
| Ghent legacy image URL fails | Use the Ex Libris service resolved by `iiif.py`. |
| BnF (Gallica) image returns HTTP 403 | The manifest's `gallica.bnf.fr/iiif` address blocks scripts. The helpers rewrite it to `openapi.bnf.fr/iiif/image/v3`, which serves the same image; it does not upscale, and takes `full/max`, not `full/full`. |
| Gallica region crop contains the wrong area | Download the full image and crop locally; record the transform. |
| Upscaled IIIF request fails | Request native resolution; the helper caps scaling at 2. |

For a record with more than a few images, look at all of them first:
`uv run --group images python tools/contactsheet.py F-xxxx /tmp/sheets` lays every
canvas out as labelled thumbnails, a few to a sheet. Use the sheets to see which
images carry the fragment, which are host pages or blanks, and where headings
are, then fetch native crops of the chosen areas only. Thumbnails are for layout,
not for transcription.

Start with a whole-face overview when available, then select native-resolution
crops of useful headings, openings and surrounding prose. Include the overview
in the neutral packet so the reader can distinguish layout from a crop's edges.
The packet prompt asks for a short layout survey followed by selected readings.
An overview is for structure; use the native crops for small letterforms. If a
crop proves uninformative, request the adjacent area without exposing a candidate
answer. Preserve the actual inputs and response, including limited coverage.

## Prepare an isolated packet

```sh
uv run python tools/readings.py packet /tmp/reading-packet /tmp/crops/column-a.jpg /tmp/crops/column-b.jpg
```

The new directory contains neutral image names, `PROMPT.md`, and `packet.json`
with image/prompt checksums. Pixels are copied unchanged. Keep the packet outside
the repository and the ordered source-to-neutral-name mapping with the coordinator.

Launch a fresh reader session with that directory as its working directory and
only its prompt and images as inputs. Allow image viewing and response writing;
do not supply search access, repository access, or inherited conversation. Check
its inputs/activity before attesting to isolation. A new turn in the same chat
is not a fresh session. If exposure is reported, retain it as a limitation; use
a fresh reader only if genuine isolation is available.

Save the complete UTF-8 response, including limitations, as `/tmp/first-reading.txt`.
The packet prompt specifies physical line labels and uncertainty notation.

## Freeze and commit before candidate discovery

Register the fragment in `data/fragments.json` before saving a reading
(`tools/register.py --cache /tmp/source-images F-xxxx ...` writes the row from the
cached manifest, as unidentified, with a placeholder note). A report
is not required: the preservation tool creates the fragment's readings directory.
Unresolved attempts can retain their evidence without a public writeup.


```sh
uv run python tools/readings.py freeze F-eo5z first-01 \
  --packet /tmp/reading-packet --text /tmp/first-reading.txt \
  --reader 'model and version' --session 'fresh-session-reference' \
  --image-source 'IIIF URL or canvas and region for image-001' \
  --image-source 'IIIF URL or canvas and region for image-002' \
  --attest-isolated
uv run python tools/readings.py check
git add fragments/F-eo5z/readings/first-01.json
git commit -m 'Preserve image-only reading for F-eo5z'
```

Supply one public `--image-source` citation per image, in packet order, and an
opaque session reference. The command verifies packet hashes and creates a new
record with exact response text, prompt, image provenance, reader, time, and
checksums. It refuses overwrites. It does not launch or sandbox the reader:
`--attest-isolated` is the coordinator's assertion, not a software guarantee.

## Save a substantive assisted revision

```sh
uv run python tools/readings.py revise F-eo5z assisted-01 \
  --first first-01 --text /tmp/revised-reading.txt \
  --reader 'model and version' \
  --source 'Edition or reading citation and page/line locus' \
  --reason 'Expanded an uncertain abbreviation after comparison'
```

The base must be an existing image-only or HTR record. Repeat `--source` for the
readings and editions used; cite intermediate revisions if applicable. The new
record links to the base by name and checksum. Corrections do not replace the base.
Link saved records in the report with their actual labels and full GitHub file
URLs so the site renderer makes them clickable.

## Preservation checks

```sh
uv run python tools/readings.py check --base origin/main
```

This validates record contents/references and byte-for-byte preservation against
the base commit, including deletion and renaming. CI compares against the PR base
or previous main commit. Review of the first record still needs to establish that
the isolation and freeze-before-search procedure was followed. HTR is optional;
its commands are in [HTR.md](HTR.md).
