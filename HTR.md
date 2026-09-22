# A second image reader: Kraken and CATMuS Medieval

Run HTR on the same neutral image packet as the independent LLM reader. Each reads
only pixels; neither sees the other's output before its response is preserved.
After both are saved, inspect disagreements against the image. Agreement is not
certification, and neither reader's fluent text is a reason to replace the other.

This uses [Kraken](https://github.com/mittagessen/kraken) 7.1.1 and
[CATMuS Medieval](https://zenodo.org/records/21488839), by Ariane Pinche, Thibault
Clérice, Malamatenia Vlachou-Efstathiou and collaborators (CC-BY-4.0). The model
includes Latin and transcribes graphemes without expanding abbreviations. Its
release record says 1.6.2 while the filename says 1.6.0; `htr/models.json` pins the
record, file and SHA-256 rather than guessing from the filename. The bundled
Kraken baseline segmentation model is pinned by hash too.

## Setup and run

From the repository root:

```sh
uv sync --project htr --python 3.12 --frozen
uv run --project htr --frozen python tools/htr.py download-model scratch/htr-models
uv run --project htr --frozen python tools/htr.py run \
  --packet /tmp/reading-packet --model-dir scratch/htr-models \
  --output scratch/htr/run-01
```

Create the packet using [FIRST_READINGS.md](FIRST_READINGS.md). Prefer native
resolution, upright column images with sufficient context; tight, enlarged crops
can defeat segmentation. Select crops using layout, not which output agrees with
a proposed edition. Record any crop or orientation change as a new input. This
runner applies no image preprocessing, binarization, or spelling correction.

Kraken runs locally on CPU, one thread, with no candidate text or edition input.
The separate `htr/uv.lock` records its dependency environment. Routine repository
tests/builds do not install PyTorch. We tested inference on macOS ARM64; the
normal Linux CI tests the adapter and artifact contracts without loading models.
No GPU or eScriptorium server is required.

Outputs, in a new directory (existing directories are never reused):

- `raw/*.xml`: untouched PAGE XML, including line polygons, baselines, and text.
  Word/glyph subdivision is disabled; no confidence scores are used.
- `run.json`: raw XML with checksums, image hashes, model identities/hashes,
  engine/package versions, settings, warnings, and a labelled raw transcript.
- `transcript.txt`: the same raw line text, retaining combining marks and spacing.
- `review.html` and local `images/`: line polygons/numbers over the input image,
  alongside recognized text. Open this file to check segmentation and reading
  order. Numbers identify detections, not verified physical manuscript lines.
- `raw/*.log`: local diagnostics; do not publish logs with local paths.

A zero-line result saves diagnostics and exits with status 2. It cannot be frozen.
A subprocess failure exits with status 1 and leaves diagnostics without a complete
`run.json`. Blank recognized lines are retained and flagged. A nonempty result can
still omit, merge, split, or reorder physical lines; inspect the overlay even when
there are no machine-detected warnings. No automatic error rate is asserted.

## Preserve and compare

```sh
python3 tools/readings.py freeze-htr F-eo5z htr-01 \
  --run scratch/htr/run-01/run.json --purpose independent-reading \
  --image-source 'IIIF URL or canvas/region for the first image'
python3 tools/readings.py check
git add fragments/F-eo5z/readings/htr-01.json
git commit -m 'Preserve independent HTR reading for F-eo5z'
```

Repeat `--image-source` for every packet image, in order. The saved record has kind
`htr`, distinct from an LLM's `image-only` record: it makes no false claim about a
fresh chat session or use of the LLM prompt. `--purpose tool-validation` marks a
software trial using a previously studied passage. Existing raw records remain
protected by the same checksum and Git-base checks from change #1. The raw XML is
embedded in the record, so no images or weights need to be committed.

Save the independent LLM reading with `readings.py freeze` before showing it the
HTR. Then compare both saved readings with the images, using polygons to resolve
line correspondences. Do not equate HTR detection numbers with the LLM's physical
line numbers automatically. Keep unresolved alternatives visible. If a model has
seen HTR output, its next response is an assisted review, not another independent
reading. Preserve a resulting correction with `readings.py revise`, citing both
readings and any edition consulted; that command can reference an HTR record.

## Keep raw, expanded and search text separate

Proposed expansions are optional, keyed by HTR detection ID. For example, an
`expansions.json` file could contain:

```json
{
  "image-001.jpg:L001": {
    "text": "proposed expanded text?",
    "uncertain": true,
    "basis": "Explain the image evidence and cite any other reading or source used"
  }
}
```

```sh
python3 tools/htr.py layers --run scratch/htr/run-01/run.json \
  --expansions /tmp/expansions.json --output /tmp/layers.json
```

The output references the raw run's checksum and carries three distinct fields
per line: unchanged `raw`, optional `proposed_expansion`, and `search_text` with
an explicit `search_basis`. Uncertainty and its rationale remain attached to the
expansion. No expansion is invented for omitted lines. Search text only composes
Unicode and collapses whitespace; abbreviation marks and uncertainty markers stay.
Latin spelling variants, fuzzy retrieval, and search ranking belong to change #3.
The derived layers are working aids, not certified readings. Save substantive
revised readings with `readings.py revise` if they enter a report.

The [F-eo5z trial](audits/htr-2026-09-22.md) records what this implementation
actually produced, including segmentation failures. It is not a completed pilot
or a re-adjudication of the manuscript.
