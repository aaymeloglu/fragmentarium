# Fragment identification: research brief

You are identifying the text on manuscript fragments that fragmentarium.ms
catalogues as unidentified. For each fragment assigned to you, find the work
(author, title, locus) if it can be found, and prove it by comparing the
manuscript with the source. This is model work; be exact about what you checked.

## Materials

- Repository checkout, read-only for you: `<checkout>`. Read `METHOD.md` and
  `CONVENTIONS.md` once; `RETRIEVAL.md` lists the search sources. Do not edit,
  commit or push anything.
- The isolated first reading of each fragment, made from images alone,
  unverified and often wrong in places:
  `fragments/<F-id>/readings/<batch>-image-only.json` (field `text`;
  `packet.images[].source` cites the image regions it saw).
- Cached native images and the manifest: `<cache>/<F-id>/`. The cache holds only
  the first few images of a record.

## Before reading

1. Read the catalogue's own description in `<cache>/<F-id>/catalogue.txt`: title,
   folio reference, reconstruction summary, dimensions, the canvas labels, and
   any full description linked from the record page, which can name texts the
   title calls unidentified.
   Settle which object in the images is the catalogued fragment (host pages,
   covers and neighbouring leaves often belong to other records) and what the
   catalogue already identifies, including under sibling records of the same
   volume. Your result must be about the unidentified part, and your report
   must say what the catalogue already knew.
2. Run `uv run python tools/iiif.py <F-id> info`. It lists every image and
   reports any the catalogue links wrongly. For a record with more than about
   eight images, make contact sheets first
   (`uv run --group images python tools/contactsheet.py <F-id> <evidence>/<F-id>/sheets`),
   pick the headings, openings and a few connected passages, and read those.
   Do not read every line of a long record before the first search.

## Reading

Cut crops with `tools/iiif.py <F-id> crop ...` or, from a cached image,
`uv run --group images python tools/localcrop.py SRC OUT x0,y0,x1,y1` (or
`--strips`). Read at reading size: bands of ten to twenty lines, one column
wide. Reread and correct the first reading; say which lines you read yourself.
Look at every leaf and face before characterising the fragment.

## Searching

- Local search service `http://127.0.0.1:8790`: `/gb?q=` Google Books (quote
  phrases, URL-encode), `/ia?q=` Internet Archive full text, `/cc?q=&index=p`
  Corpus Corporum (accepts `NEAR/N`). Google Books has a daily quota and fails
  intermittently; when it does, use the others.
- `tools/mdzsearch.py '"phrase" "phrase"'`: OCR full text of the Munich digital
  library, strong for anything printed between 1470 and 1700.
- `tools/gbwithin.py <volume id> '"phrase"'`: inside one Google Books volume.
- `tools/mnlsearch.py 'phrase'`: the Corpus Middelnederlands, for Middle Dutch.
- `tools/schneyer.py` (sermon repertory), `tools/hspsearch.py` (German
  manuscript catalogues), `tools/gw.py <GW number>` (digitised incunables).
- Web search and fetch for everything else: Corpus Thomisticum, Gloss-e,
  archive.org, e-codices, Gallica, DigiVatLib, Biblissima and ARCA, Cantus,
  Analecta Hymnica, and library catalogues.
- Never fetch books.google.com page or image addresses: that triggers captchas
  that break the search service for everyone. If a source is blocked, say so
  and move on.

Search distinctive connected prose of four to eight words, not biblical
quotations or formulas. A hit is a lead.

## Proving it

Once a candidate passage is located, read the source itself (page image where
one exists; say so when you had only OCR, a transcription or snippets) and
collate at least two separate manuscript passages against it, from different
faces or columns where possible, quoting manuscript and source side by side.
List every material difference.

Decide which layer matched: the containing work, or a source it quotes or
reworks. If the text is a compilation, abridgement or commentary built on your
match, the match is its source and the containing work is still to find. Check
the attribution of the edition or manuscript you compared against.

Claim only what the comparison shows:

- "Identified" needs sustained agreement in distinctive wording and sequence
  with a specific text and locus that you compared yourself. A source, a base
  text or a genre is "partial". Otherwise "unidentified". Never upgrade a result
  to make it publishable.
- Agreement of catalogue records (same owner, same sale, similar size) makes a
  candidate, not an identification.
- Differences from a printed edition (spelling, omissions, better readings) do
  not show that a manuscript is independent of it. Leave that open unless you
  have evidence that bears on it.

## Limits

About 150 tool calls a fragment, in several rounds if needed. Do the reading
yourself; do not hand a record out to further agents. If you have no candidate
to test after about 80 calls on one fragment, write up what you have and stop.
Do not stop while a named candidate is untested: read it on the page first.
Save the crops and source pages you relied on under `<evidence>/<F-id>/`.

## Report

Write `<research>/<F-id>.md`:

1. Verdict: identified, partial or unidentified, with author, work, locus and
   a link to the edition or manuscript.
2. What the catalogue already knew.
3. What the fragment is physically, which images show what, and which parts
   you read.
4. Assisted reading: the manuscript lines you rely on, with canvas number and
   native-pixel box, uncertainty marked.
5. Comparison: manuscript against source, side by side; differences; the kind
   of source evidence and its address.
6. Basis for the source's attribution.
7. Candidates tested and rejected, with reasons; sources that were unavailable.
8. What remains open and what would resolve it.
9. A ledger note of two to four plain sentences.

Your final message: three or four lines per fragment giving the verdict, the
key evidence and the main doubt.
