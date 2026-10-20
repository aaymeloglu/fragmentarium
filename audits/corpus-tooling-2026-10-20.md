# Public OCR corpus: acquisition and retrieval check, 20 October 2026

Fetched all twelve sources in [the collection](../data/corpora/homiletic.json):
48,716,360 bytes (46.5 MiB) of UTF-8 OCR. Downloads agreed with IA's
file sizes and SHA-1 metadata; the collection pins the resulting SHA-256 values.
The local cache holds acquisition receipts and the original text bytes. No books,
page images or full metadata dumps are committed.

The collection covers PL 39, 40, 76, 94, 95, 117, 131 and 165; Graesse's
*Legenda aurea* (1846); Bromyard's *Summa praedicantium* I-II (1586); and
Petrus Hieremia's *Divinum opus* (1502). Coverage labels were checked against
catalogue metadata and OCR preliminaries, not a complete page-image collation.
Historical author labels do not resolve disputed attribution.

## Full-corpus retrieval control

The [saved query and result](corpus-control-2026-10-20.json) use a passage from
the Silvester opening in the known Graesse edition. The first anchor contains
`bonae terrae`, a bounded gap, and `humiliatiomis` (deliberately corrupted from
`humiliationis`). The second anchor is `dulcedinem devotionis`.

Searching all twelve volumes with `--max-edits 1 --window 600` recovered both
anchors in order in *Legenda aurea*, with the deliberate typo requiring one edit
and the gap measuring 47 normalized characters. The source offsets and exact
OCR excerpts remain in the result. Bromyard II matched the second anchor only;
that shorter parallel did not outrank the complete passage.

This is a source-assisted engineering control, not a new fragment identification,
a blind transcription trial or an estimate of identification yield. The test
establishes that acquisition feeds the existing fuzzy/gapped matcher correctly.
The OCR remains noisy, and there are no checked physical page mappings yet.

## Validation

119 tests passed, including failed/restricted downloads, ambiguous OCR files,
checksums, resumable import and an end-to-end gapped search of fetched bytes.
Re-running the fetch command reuses the checked local text. The existing matcher
and publication data are unchanged. See [usage and limits](../tools/CORPUS.md).
