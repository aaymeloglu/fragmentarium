# Fragmentarium: identifying the unidentified

[Fragmentarium](https://fragmentarium.ms/) is the international database of medieval manuscript
fragments, the leaves and strips cut from old books and reused as binding waste. A sweep on
20 September 2026 found 222 records with "unidentified" in the title or summary
([saved corpus list](data/unidentified-2026-09-20.csv)). This repository works through them: read the fragment from
the library's images, find the text in a printed edition or a digital corpus, and write the
comparison out so anyone can check it.

The [results table with thumbnails](https://aaymeloglu.github.io/fragmentarium/) is on the project site. Each row
links to a report with readings, comparisons, source links, and remaining questions. The
[burndown list](https://aaymeloglu.github.io/fragmentarium/burndown.html) includes all 222 records,
marks those already examined, and gives a rough search priority based on language, size, date,
and genre. Records whose descriptions omit "unidentified" are outside this list.

## Results so far: 22 fragments, 8 identified, 12 partial, 2 not identified

| Fragment | Catalogued as | Result | Identification confidence |
|---|---|---|---|
| [F-ss0e](fragments/F-ss0e) Antwerp, Fragm. 237 | theological treatise, 11th c. | Passage parallel to Cherubino da Spoleto, Sermones quadragesimales; compiling text and attribution unresolved | partial, medium |
| [F-1exy](fragments/F-1exy) Toruń, Rps 65/V | Genesis commentary | Nicholas of Lyra, Tractatus de differentia nostrae translationis ab hebraica littera, Genesis section | identified, high |
| [F-2e1n](fragments/F-2e1n) Bruges, reeks 538 | Latin etymology | Johannes Balbus, Catholicon, letter C | identified, high |
| [F-cfry](fragments/F-cfry) Vienna, Cod. 4070 | homily | Nicholas of Lyra, Postilla litteralis super Epistolam ad Hebraeos, chapter 5 | identified, high |
| [F-eo5z](fragments/F-eo5z) Ghent, HS.2582/290 | natural philosophy | Richard of Middleton, Quaestio disputata de gradu formarum; leprous-parent and asses arguments | identified, high |
| [F-s8db](fragments/F-s8db) Park Abbey, IIIB1.429 | gloss on canon law | Guido de Baysio, Rosarium super Decreto, C.10 q.1 c.13 | identified, high |
| [F-jaob](fragments/F-jaob) BnF, lat. 9377 ff. 70-73 | Sentences IV commentary | Anonymous Sentences IV epitome combining mnemonic verse and prose summaries | partial, medium |
| [F-3yl2](fragments/F-3yl2) Toruń, Ob.6.II.684-686 | treatise with Summa fragment | Anonymous compilation adapting Aquinas, Summa theologiae IIa-IIae q.10 a.12 and q.11 a.1 | partial, medium |
| [F-ahiy](fragments/F-ahiy) Bruges, Ms. 95/130 | encyclopaedia | Alphabetical compilation of moral authorities, with Moralium dogma philosophorum and patristic source parallels | partial, medium |
| [F-nei7](fragments/F-nei7) Ghent, HS.2582/164 | metaphysics | Anonymous scholastic questions probably relating to Sentences I; author and exact locus unresolved | partial, low |
| [F-8bin](fragments/F-8bin) BnF, lat. 9377 ff. 90-93 | De sacramento eucharistiae | Unidentified Latin didactic poem on sacramental themes, with an apparent dieta transition | not identified |
| [F-lmfj](fragments/F-lmfj) Oudenaarde, Hs. 20/5 | medical text with gloss | Hippocrates, De regimine acutorum, with Galen commentary in the Latin Articella tradition | identified, high |
| [F-o1p7](fragments/F-o1p7) Oudenaarde, BB 0027 | Roman law | Bernardus Compostellanus iunior, Lectura in primum librum Decretalium, De electione | identified, high |
| [F-8bfm](fragments/F-8bfm) Toruń, Ob.6.II.2164-2173 | theological treatise | Robert Holcot, Super Sapientiam Salomonis, end of lectio II and part of lectio III | identified, high |
| [F-h8oz](fragments/F-h8oz) Oudenaarde, nr. 56 | canon law | Anonymous procedural text with a close Durantis, Speculum iudiciale II.3, De appellationibus parallel | partial, medium |
| [F-szxp](fragments/F-szxp) Leipzig, Fragm. lat. 52 | medical fragment | Medical compilation on sleep, with Hippocratic and other source layers; compiler unidentified | partial, medium |
| [F-072h](fragments/F-072h) Leuven, Ms. 1206 | medical treatise | Commentary around Hippocrates, Aphorisms VII.54–59, plus a medical chapter table; compiling work unresolved | partial, medium |
| [F-b8xt](fragments/F-b8xt) Bruges, Fragm. 27 | philosophical text | Anonymous Metaphysics questions with sustained Aquinas, Sententia libri Metaphysicae VII lect.4 nn.3–4 parallels | partial, medium |
| [F-nxl7](fragments/F-nxl7) Bruges, Ms. 466 | treatise on physics | Anonymous questions on longevity, natural heat and moisture in the Parva naturalia tradition | partial, low |
| [F-0kql](fragments/F-0kql) Park Abbey, VIIIB20/51 | life of Gregory the Illuminator | Latin life of Gregory the Illuminator in the Agathangelos tradition; exact Latin recension unresolved | partial, low |
| [F-hcpv](fragments/F-hcpv) Park Abbey, VIIIB20/52 | legend of Gregory the Illuminator | Ending of a Latin life of Gregory the Illuminator; exact Latin recension unresolved | partial, medium |
| [F-2a37](fragments/F-2a37) Locarno, MdS 38 Fa 31 | commentary on a religious text | Unidentified, heavily worn text; a scholastic lemma-and-exposition commentary is plausible | not identified |

Confidence in the table concerns the identification or proposed source connection only.
These labels do not certify transcription accuracy or imply that every passage has been verified.

Research and review were performed by LLMs. The reports give selected source-assisted manuscript
readings, comparisons, and unresolved questions, with separate preserved image-only readings
and, where used, HTR output. No full transcription or measured transcription accuracy is claimed;
the recorded image checks are not human palaeographic verification.

The eight identifications rest on selected manuscript passages compared with printed sources.
Bernardus's commentary was checked against the 1516 print images. Richard of Middleton was
compared with Hocedez's printed excerpts; the complete edition and apparatus remain unchecked.
For partial findings, the evidence varies by report: print images, edition OCR, electronic Latin
texts, or, for the Cherubino parallel, a printed snippet. A source connection can be supported
while the compiling work remains unidentified.

The linked fragment reports give the scope, evidence, and remaining limits for each result.
See [CONVENTIONS.md](CONVENTIONS.md) for status definitions and [METHOD.md](METHOD.md) for the
research process. Failure to find a text in the recorded searches does not establish that it
is unprinted or a new witness.

## Working here

Start with [AGENTS.md](AGENTS.md). [METHOD.md](METHOD.md) is the short research
workflow and [CONVENTIONS.md](CONVENTIONS.md) defines the evidence standards.
Image/reading, HTR, and retrieval manuals are references for the task at hand,
not prerequisites to read or execute in full.

## Layout

```
data/fragments.json            one row per fragment: catalogue data, our result, confidence, links, thumbnail URL
data/unidentified-*.csv        the corpus list, from a sweep of Fragmentarium's search
fragments/<F-id>/README.md     selected readings, source comparisons, evidence limits, open questions
docs/                          the site; python3 docs/_build_site.py regenerates it (stdlib only)
tools/searchd.py               local search service: Google Books, archive.org full text, Corpus Corporum on localhost (holds the key)
htr/models.json               pinned recognition and segmentation model identities
pyproject.toml + uv.lock       one Python 3.13 environment; optional htr dependency group
tools/latin_search.py         tolerant Latin retrieval with original offsets and ordered passage ranking (see RETRIEVAL.md)
tools/htr.py                  Kraken/CATMuS runner, segmentation review, separate text layers (see HTR.md)
tools/readings.py              neutral image packets, preserved first readings, separate source-assisted revisions
FIRST_READINGS.md             isolated-reader procedure and command examples
tools/iiif.py                  fetch a fragment's images: info, overview, tiles, crop; resolves each library's IIIF quirks
tools/ia_cluster.py            do the anchor phrases sit in one passage of an archive.org volume's OCR?
tools/gbsearch.py              Google Books full-text search from the command line (needs GOOGLE_BOOKS_API_KEY)
tests/                         data/folder/site consistency; CI fails if docs/ is stale
```

No images are stored here. Thumbnails on the site are served by the holding libraries' IIIF
servers; rights stay with the institutions named on each record.

## Reporting

For catalogue submissions, use Fragmentarium's own field names and address fragmentarium@unifr.ch
with the holding library copied, as described in [CONVENTIONS.md](CONVENTIONS.md). Include the
relevant comparison and its limits; research runs do not send submissions automatically.
