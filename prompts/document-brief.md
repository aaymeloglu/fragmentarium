# Archival documents: research brief

You are working on fragments of archival documents (deeds, charters, letters,
grants of arms, copies of documents) that fragmentarium.ms catalogues only by
type and date. Find what each document says and whether it is recorded
elsewhere. This is model work; be exact about what you checked.

## Materials

- Repository checkout, read-only for you: `<checkout>`. Read the status rules
  in `CONVENTIONS.md`, including "Archival documents". Do not edit, commit or
  push anything.
- Native images in the image cache, `<cache>/<F-id>/canvas-N-w*.jpg`. If a
  record's canvases are not all there, run
  `uv run python tools/iiif.py <F-id> cache`.
- `uv run python tools/catalogue.py <F-id>`: the catalogue's text, and any
  attached transcription. Read an attached transcription only after your own
  reading.

## Before reading

1. Look at every canvas reduced. The image labelled "r" is often the back:
   decide which face carries the text. The back has endorsements, modern
   pencil notes, removal labels and the binding's title; read them, but treat
   them and the catalogue's date and type as leads to confirm, not evidence.
2. Count the documents. A "deed" can be a copy sheet with several documents,
   each opening with its own intitulatio ("Wir ... von gottes genaden",
   "Ich ..."). Report each separately.
3. Original, copy or draft: seals or seal slits, signatures, chancery notes,
   blank spaces left for painted arms, deletions.

## Reading

Read at native size, bands of about ten lines, usually half the width
(`uv run --group images python tools/localcrop.py SRC OUTDIR --strips N
--columns 2`; add `--autocontrast`, or `--channel b --equalize` for faded ink).
Cite native-pixel boxes. For each document transcribe the protocol (issuer,
titles, addressee), enough of the disposition to state the legal action,
parties, places and objects, and the whole dating clause. Expand abbreviations
in parentheses; mark uncertain readings (?) and losses [...]. Do not let an
outside record decide a reading you could not make; say which readings rest on
it.

Convert the dating clause yourself: `uv run python tools/feastdate.py YEAR
"Montag vor Jacobi"` (Julian before 1583 by default). When the year is lost,
regnal years can date the document (for an emperor, the Roman, Hungarian and
Bohemian years); say how you counted them. Check the date against the
document's own evidence: the titles it gives a ruler or official, offices held,
people's lifetimes. A year read as 1525 in a document calling Ferdinand Roman,
Hungarian and Bohemian king is wrong (he took those crowns in 1526 and 1531).
Label every element of the regest that you supplied from a source instead of
reading it.

## Searching

Search by issuer, date and beneficiary, then by distinctive phrases. Which
sources can hold the act depends on its kind:

- **Rulers, estates and Landtag acts:** Regesta Imperii online; Chmel's
  editions (*Regesta Friderici III* with its Anhang, *Materialien zur
  österreichischen Geschichte*); for Tyrol, Schober, *Die Urkunden des
  Landschaftlichen Archivs zu Innsbruck* (1990), and Jäger's history of the
  Tyrolean estates.
- **Grants of arms and nobility:** K. F. von Frank, *Standeserhebungen und
  Gnadenakte*; the Austrian State Archives catalogue (archivinformationssystem.at).
  Frank's snippets name beneficiary, kind of grant, place and date.
- **Private and seigneurial acts** (tenancies, fiefs, sales): local histories,
  regional archive finding aids, fief registers. These are rarely printed;
  expect a partial result, and stop searching when no source has a specific
  reason to hold the act.
- **Full text:** the local search service (`/gb`, `/ia`) and
  `tools/mdzsearch.py` for nineteenth-century editions, which Google Books and
  the Internet Archive sometimes miss.
- monasterium.net, Regesta Imperii and the Austrian State Archives refuse
  scripted fetches. Use a browser if you have one; otherwise record them as
  not checked, not as negative.

Never fetch books.google.com page or image addresses.

## Proving it

An outside record corroborates the regest; it is not required (CONVENTIONS,
"Archival documents"). Compare the record you find with your reading, side by side: issuer, date,
place, beneficiary, substance, and wording where the record prints the text.
Read page images where they exist and say when you had only snippets. For a
copy without a year, choose between candidate acts by their content and say
so.

## Report

Write `<research>/<F-id>.md`:

1. Verdict per document, with the regest and the external record (citation,
   link) if any.
2. What the catalogue said, and what it got right or wrong.
3. Faces, documents, original or copy, back and labels, host volume.
4. The passages you rely on, with canvas and native box.
5. Each dating clause and its conversion.
6. Comparison with the external record.
7. Searches that found nothing; sources not reachable.
8. A ledger note of two to four plain sentences.

About 120 tool calls a record. Your final message: two or three lines per
document giving the verdict, the regest and the main doubt.
