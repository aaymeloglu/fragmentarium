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

## Identification status and confidence

The index's `status` and `confidence` describe support for the identification
claim only, including a provisional connection when status is partial. They do
not grade transcription accuracy, verification coverage, dating, or witness
novelty. A well-supported identification can coexist with a poor transcription.
Keep these labels tied to the stated identification rather than averaging the
strength of unrelated claims:

| Status | Meaning |
|---|---|
| **Identified** | Sustained agreement in distinctive wording and sequence identifies a text in a specific edition, with abbreviations and textual variants recorded. Give the author, work, locus, and a checkable link. The current index requires confidence `high`. |
| **Partial** | A source connection, genre, subject, or text layer has support, but the compiling work or attribution remains unresolved. Use `medium` for a substantial source parallel or text layer, `low` for chiefly genre, school, or author leads. |
| **Not identified** | Describe the fragment and searches, but no identification is established. Confidence `none`. |

## Writeup: distinguish the claim, the reading, and the checks

Write current fragment pages as standalone accounts of the present findings and
evidence. Keep review dates, changes to past claims, and run history in audits or
preserved records, rather than narrating them in the report.

Open a new or revised report with a concise evidence summary. Three short bullets
or a paragraph are enough; no additional scores or fixed table are required:

- **Identification:** state the proposed work or source connection, its status
  and identification confidence, the diagnostic basis, and material alternatives.
- **Transcription:** describe the reading's basis (image-only, HTR, or assisted),
  the passages covered, and known errors or unresolved readings. State who reviewed
  which lines against the manuscript image; if accuracy has not been assessed,
  say so. Identification confidence does not transfer to the transcription.
- **Verification:** specify which manuscript and edition passages were compared,
  by whom, and using what evidence: images, OCR, snippets, or a secondary account.
  State gaps in coverage. Expert support for an attribution is not approval of
  every transcribed word; model agreement is not human review.

For each main identification claim, give enough linked evidence to inspect it:
selected manuscript lines and their image/crop reference, the candidate text's
edition/locus and link, and significant agreements or differences. Distinguish
literal quotations from paraphrases or thematic parallels. Common formulas may
explain how a candidate was found, but the diagnostic comparison must carry the
identification. Avoid "verbatim" or "line-by-line verified" beyond the passages
actually checked. Link preserved raw readings and label unverified machine text.

Address dating, leaf order, dependence, recension, or novelty separately **when
making those claims**, with their own basis and limits. Otherwise omit them; this
is not a checklist requiring research into every dimension. Report the checks
performed rather than creating new searches or verification work to fill headings.
Missing evidence remains explicit and limits the conclusion. No character/word
accuracy rate should be invented without a suitable checked reference.

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
identification confidence, links, order, and examination date. `docs/_build_site.py` renders the
site; CI checks record preservation, data consistency, and generated pages.

When outreach is explicitly requested, use Fragmentarium's catalogue field names
(Title, Subtitle, Persons, Date of origin, Script Type, Reconstruction Summary,
Bibliography), address fragmentarium@unifr.ch with the holding library copied,
and record whether the report was sent.
