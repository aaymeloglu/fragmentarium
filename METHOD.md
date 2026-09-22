# Method

How each fragment is worked. The same brief was given to every run; the order of searches matters
more than any single tool.

## 1. Images

Every Fragmentarium record has a IIIF manifest at
`https://fragmentarium.ms/metadata/iiif/<F-id>/manifest.json`. Each canvas gives an image resource
whose `@id` ends in `/full/full/0/default.jpg`; replace `full/full` with a region and size to get
crops at native resolution (`/<x>,<y>,<w>,<h>/900,/0/default.jpg`). Upscaling beyond about 2x
returns 404. Some libraries serve their images elsewhere: Ghent's manifest URLs on `adore.ugent.be`
return 404 and the working endpoint is the ExLibris `service` `@id` inside the canvas; the BnF
fragments resolve to Gallica's IIIF. Read from crops, not from the overview image, and transcribe
line by line before searching anything.

Use the [first-reading workflow](FIRST_READINGS.md): a fresh reader session sees only a
neutral image packet and the reading prompt. Preserve its complete response with
`tools/readings.py freeze` and commit it before revealing candidates or consulting editions.
Save any later source-assisted reading separately with `tools/readings.py revise`.
The coordinator must not pass its own conversation or the existing fragment report to the reader.
Existing reports have not been retrospectively certified as image-only readings.

Run the [Kraken/CATMuS second reader](HTR.md) on the same image packet, preserving
its raw output with `readings.py freeze-htr`. Keep it separate from the isolated LLM
reading until both are saved. Inspect line segmentation and disagreements against
the images; do not let either reader silently rewrite the other. Raw recognition,
proposed expansions, and normalized search text remain distinct layers.

## Tools

- `python3 tools/iiif.py F-xxxx info | overview DIR | tiles DIR --canvas N --cols 2 --rows 4 | crop DIR x,y,w,h`
  resolves the working image base (Fragmentarium's own server, ExLibris for Ghent, Gallica for the
  BnF, sharedcanvas for Bruges) and fetches overviews, a grid of 2x crops, or one region. Tile a leaf
  first, then read the tiles in order; it replaces the five or six exploratory crops each run used
  to spend.
- `GOOGLE_BOOKS_API_KEY=... python3 tools/searchd.py` runs a search service on 127.0.0.1:8790 that
  answers `/gb?q=`, `/ia?q=` and `/cc?q=&index=p` with JSON, paces Google Books, and caches. Worker
  sessions query localhost and never handle the key; one process serves any number of them.
- `python3 tools/ia_cluster.py IDENT "phrase" "phrase" ... --show` downloads a volume's OCR once and
  ranks anchors in reading order within a bounded passage, with original-text offsets.
  [RETRIEVAL.md](RETRIEVAL.md) covers partial words, explicit expansion alternatives, bounded
  edit-distance matching, competing texts, and common-phrase exclusions. A full match is a
  passage to inspect, not an identification.

## 2. Searches, in this order

1. **Google Books full text.** It covers the early printed editions where most medieval texts
   that were ever printed live, and it supplied several identifications and corroborating parallels here. Other identifications, including the Articella passage, were located through Internet Archive OCR. Query with two to four distinctive quoted phrases of the fragment's own connecting
   prose (not scripture), trying u/v and ae/e spellings. The API needs a key (`tools/gbsearch.py`);
   it returns snippets and volume ids, not pages. Do not scrape the books.google.com site itself:
   a burst of page requests gets the whole network captcha-walled for hours.
2. **archive.org full text** (`be-api.us.archive.org/fts/v1/search?q=`), then the hit volume's
   `_djvu.txt`, checking ordered anchor matches with `tools/ia_cluster.py`. Search-normalized
   matches retain original text and offsets; use `--max-edits 1` for a small OCR-error allowance.
   Long-s is normalized; OCR f/s conflation requires `--ocr-long-s`. Compare downloaded
   competing works with `tools/latin_search.py` and mark common formulas explicitly.
   Google Books scans are often mirrored
   as `bub_gb_<volume id>` with better OCR than the original.
3. **Corpus Corporum** (Patrologia Latina and much else):
   `mlat.uzh.ch/php_modules/fulltext_search.php?query=...&index_type=p`, which accepts Sphinx
   `NEAR/N`. Zero hits there for a scholastic text means little; the corpus thins out after 1200.
4. **Genre-specific corpora**: Corpus Thomisticum (Aquinas, greppable HTML), Gloss-e (Glossa
   ordinaria, Hugh of St Cher, Catena aurea), Friedberg's Corpus iuris canonici on archive.org for
   the Decretum and Decretals, the Quaracchi Bonaventure and Borgnet Albert on archive.org.

The first fragment (F-ss0e) produced a useful Google Books parallel after searches in medieval corpora. The second-model review retained that parallel but qualified attribution and dating: identifying a passage in a later sermon collection does not establish its original author or the date of this copy.

## 3. Verification

Identified means sustained agreement in distinctive wording and sequence with an edition, with variants recorded and a reproducible comparison. Original research was performed by Claude, followed by lead-LLM manuscript-image spot-checks. Codex performed a second-model review on 20 September 2026. Eight identified entries have support in sampled manuscript/edition comparisons; the Bernardus comparison used edition OCR, not inspected print page images. Cherubino is a provisional textual parallel. The other reports received an evidence and reasoning audit, not a full fresh collation.

These are LLM checks, not human palaeographic verification. Full transcription accuracy, all passage endpoints, physical reconstruction, dating, literary dependence, and witness novelty have not been certified. See [review scope and evidence](https://github.com/aaymeloglu/fragmentarium/blob/main/REVIEW.md).

## 4. Choosing the next fragment

`docs/burndown.html` ranks every record in the corpus list by a rough printability score: Latin,
a large piece, 13th to 16th century, and a genre keyword that suggests a printed tradition (law,
gloss, commentary, sermon, postil, lexicon, summa, sentences, breviary, legend, medicine, logic).
It is a prior, not a prediction: the compilations and indexes that stall are often large Latin
leaves too. Work down the list; mark each attempt in `data/fragments.json` whatever the outcome,
so the negatives are recorded.

## 5. What the results look like

The current results are 8 identified, 12 partial, and 2 not identified. Several extended prose matches identify printed works, while compilations, epitomes, indexes, and school commentaries often yield source parallels without an exact work attribution. No-hit searches do not establish that a work never reached print. Some results refine broad catalogue descriptions; proposed changes to date, genre, or physical reconstruction must be justified individually.