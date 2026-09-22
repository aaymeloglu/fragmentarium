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

Use native pixels for recognition (`--scale 1`); magnification adds no evidence.
Record the public image URL or manifest, canvas, region, and any transform. Check
that the resulting crop contains the intended text. Common acquisition problems:

| Symptom | Practical next step |
|---|---|
| Ghent legacy image URL fails | Use the Ex Libris service resolved by `iiif.py`. |
| Gallica region crop contains the wrong area | Download the full image and crop locally; record the transform. |
| Upscaled IIIF request fails | Request native resolution; the helper caps scaling at 2. |

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
