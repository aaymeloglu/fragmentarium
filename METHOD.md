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
  reports whether the anchors cluster in one passage (long-s, u/v and ae/e tolerant). A full score
  is a passage to read; scattered singles across a folio volume are noise.

## 2. Searches, in this order

1. **Google Books full text.** It covers the early printed editions where most medieval texts
   that were ever printed live, and it is where every identification in this repository was made
   or confirmed. Query with two to four distinctive quoted phrases of the fragment's own connecting
   prose (not scripture), trying u/v and ae/e spellings. The API needs a key (`tools/gbsearch.py`);
   it returns snippets and volume ids, not pages. Do not scrape the books.google.com site itself:
   a burst of page requests gets the whole network captcha-walled for hours.
2. **archive.org full text** (`be-api.us.archive.org/fts/v1/search?q=`), then the hit volume's
   `_djvu.txt`, checking that all anchor phrases sit within one passage rather than scattered
   through the book. Pre-1800 prints: match `[sſf]` for s. Google Books scans are often mirrored
   as `bub_gb_<volume id>` with better OCR than the original.
3. **Corpus Corporum** (Patrologia Latina and much else):
   `mlat.uzh.ch/php_modules/fulltext_search.php?query=...&index_type=p`, which accepts Sphinx
   `NEAR/N`. Zero hits there for a scholastic text means little; the corpus thins out after 1200.
4. **Genre-specific corpora**: Corpus Thomisticum (Aquinas, greppable HTML), Gloss-e (Glossa
   ordinaria, Hugh of St Cher, Catena aurea), Friedberg's Corpus iuris canonici on archive.org for
   the Decretum and Decretals, the Quaracchi Bonaventure and Borgnet Albert on archive.org.

The order was learned the hard way: the first fragment (F-ss0e) cost a day searching the medieval
corpora on the assumption that "Ex hoc arguo" meant a 13th-century scholastic, and fell to Google
Books in one query once a key was in place. It was a 15th-century preacher.

## 3. Verification

Identified means consecutive lines match an edition verbatim, with the comparison written out in
the folder and a link that lets anyone check it. Every identification claimed by an automated run
was checked again by a person against the fragment image before it went on the index.

## 4. Choosing the next fragment

`docs/burndown.html` ranks every record in the corpus list by a rough printability score: Latin,
a large piece, 13th to 16th century, and a genre keyword that suggests a printed tradition (law,
gloss, commentary, sermon, postil, lexicon, summa, sentences, breviary, legend, medicine, logic).
It is a prior, not a prediction: the compilations and indexes that stall are often large Latin
leaves too. Work down the list; mark each attempt in `data/fragments.json` whatever the outcome,
so the negatives are recorded.

## 5. What the results look like

Of the first eleven fragments, the six identified were all much-printed works (Nicholas of Lyra
twice, the Catholicon, Richard of Middleton, Guido de Baysio, Cherubino da Spoleto). The partials
were all compilations, abridgements and indexes that never reached print: their sources pin down
fast, and then the next step is a manuscript catalogue and reading by eye, which searches cannot
do. In every identified case the catalogue's genre or date label turned out to be wrong, not just
missing.
