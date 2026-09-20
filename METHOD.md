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

## 4. What the results look like

Of the first eleven fragments, the six identified were all much-printed works (Nicholas of Lyra
twice, the Catholicon, Richard of Middleton, Guido de Baysio, Cherubino da Spoleto). The partials
were all compilations, abridgements and indexes that never reached print: their sources pin down
fast, and then the next step is a manuscript catalogue and reading by eye, which searches cannot
do. In every identified case the catalogue's genre or date label turned out to be wrong, not just
missing.
