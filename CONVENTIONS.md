# Evidence and reporting standards

These are the required standards for research claims. [METHOD.md](METHOD.md)
provides adaptable research tactics; the tool manuals describe commands.

## Evidence rules

- Base transcription claims on inspected manuscript images. Keep uncertainty,
  gaps, corrections, and physical line references visible. Distinguish raw
  recognition, proposed expansions, and search-normalized text.
- An independent image-only reading uses a fresh reader with no proposed answer,
  earlier transcription, edition, or other reader's output. Preserve the complete
  response and its input provenance, and commit it before candidate searching or
  comparison. [FIRST_READINGS.md](FIRST_READINGS.md) gives the procedure. If
  independence cannot be established, label the work assisted and state the
  limitation; do not claim a blind reading. Existing reports are not
  retrospectively certified as independent.
- Never edit or delete a preserved reading. Save substantive assisted revisions
  separately, citing the readings and sources used. Corrections to saved metadata
  also belong in a new record or audit note. Checksums protect preservation, not
  the truth of a reading or the reader's isolation.
- A search hit, retrieval score, common phrase, or agreement between readers
  establishes a lead, not an identification. Support identification with sustained
  distinctive wording and sequence, documenting differences. Shared biblical
  quotations and formulas are not diagnostic anchors on their own.
- Say what was checked and what was not, including whether comparison used images,
  OCR, snippets, or secondary paraphrase. Do not describe LLM checks as human
  palaeographic verification. Distinguish a genuine exclusion from a no-hit search
  or an unavailable source; unsuccessful search does not establish unprinted status.
- Dating, provenance, leaf order, literary dependence, recension, and witness
  novelty need their own evidence. Identification does not certify transcription
  accuracy or those additional claims. Limit each conclusion to its support.

## Status

The current index uses these labels:

| Status | Meaning |
|---|---|
| **Identified** | Sustained agreement in distinctive wording and sequence identifies a text in a specific edition, with abbreviations and textual variants recorded. Give the author, work, locus, and a checkable link. The current index requires confidence `high`. |
| **Partial** | A source connection, genre, subject, or text layer has support, but the compiling work or attribution remains unresolved. Use `medium` for a substantial source parallel or text layer, `low` for chiefly genre, school, or author leads. |
| **Not identified** | Describe the fragment and searches, but no identification is established. Confidence `none`. |

## Report and record format

`fragments/<F-id>/README.md` contains the catalogue details, scoped reading and
comparison, sources, result, and unresolved questions. Include the lines needed
to assess the claim, with proposed expansions in parentheses and uncertainty
marked. State the coverage; do not imply unread sides were transcribed. Provide
an edition/facsimile link and locus, and use a comparison table when it helps.
Dates are absolute, for example "22 September 2026".

Link preserved `readings/*.json` records by their actual kind: image-only, HTR,
or source-assisted. Use the preservation commands when those records exist;
[HTR.md](HTR.md) covers raw recognizer output. If isolation was unavailable and
there is no independent base record, keep the assisted text and its provenance
in the report or a separate labelled file outside `readings/`; the CLI cannot
create an assisted record without a base. The report states the missing
independent evidence. Do not fabricate a base to satisfy the schema.

`data/fragments.json` holds catalogue data, identification, note, status,
confidence, links, order, and examination date. `docs/_build_site.py` renders the
site; CI checks record preservation, data consistency, and generated pages.

When outreach is explicitly requested, use Fragmentarium's catalogue field names
(Title, Subtitle, Persons, Date of origin, Script Type, Reconstruction Summary,
Bibliography), address fragmentarium@unifr.ch with the holding library copied,
and record whether the report was sent.
