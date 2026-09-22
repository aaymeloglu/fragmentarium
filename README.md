# Fragmentarium: identifying the unidentified

[Fragmentarium](https://fragmentarium.ms/) is the international database of medieval manuscript
fragments, the leaves and strips cut from old books and reused as binding waste. Of its roughly
2,850 public records, 222 are catalogued with "unidentified" in the title or summary
(`data/unidentified-2026-09-20.csv`). This repository works through them: read the fragment from
the library's images, find the text in a printed edition or a digital corpus, and write the
comparison out so anyone can check it.

The results table with thumbnails is at **https://aaymeloglu.github.io/fragmentarium/**. Each row
links to a page with the transcription, the line-by-line comparison and the links. The
[burndown list](https://aaymeloglu.github.io/fragmentarium/burndown.html) ranks every remaining
"unidentified" record by how likely a search can settle it.

## Results so far (20 September 2026: 22 fragments, 8 identified, 12 partial, 2 not identified)

| Fragment | Catalogued as | Result | Confidence |
|---|---|---|---|
| [F-ss0e](fragments/F-ss0e) Antwerp, Fragm. 237 | theological treatise, 11th c. | Cherubino sermon parallel; attribution and manuscript date unresolved | partial, medium |
| [F-1exy](fragments/F-1exy) Toruń, Rps 65/V | Genesis commentary | Nicholas of Lyra, De differentia nostrae translationis ab hebraica littera, Genesis | identified, high |
| [F-2e1n](fragments/F-2e1n) Bruges, reeks 538 | Latin etymology | Johannes Balbus, Catholicon, letter C | identified, high |
| [F-cfry](fragments/F-cfry) Vienna, Cod. 4070 | homily | Nicholas of Lyra, Postilla on Hebrews 5 | identified, high |
| [F-eo5z](fragments/F-eo5z) Ghent, HS.2582/290 | natural philosophy | Richard of Middleton, Quaestio de gradu formarum | identified, high |
| [F-s8db](fragments/F-s8db) Park Abbey, IIIB1.429 | gloss on canon law | Guido de Baysio, Rosarium super Decreto, C.10 q.1 | identified, high |
| [F-jaob](fragments/F-jaob) BnF, lat. 9377 ff. 70-73 | Sentences IV commentary | Lombard IV epitome; ps.-Bonaventure verses and prose parallels in Hus, relationship unresolved | partial, medium |
| [F-3yl2](fragments/F-3yl2) Toruń, Ob.6.II.684-686 | treatise with Summa fragment | compendium reworking Aquinas ST IIa-IIae q.10-11 with law citations | partial, medium |
| [F-ahiy](fragments/F-ahiy) Bruges, Ms. 95/130 | encyclopaedia | alphabetical tabula of authorities; some source parallels checked | partial, low |
| [F-nei7](fragments/F-nei7) Ghent, HS.2582/164 | metaphysics | anonymous Sentences I question; exact distinction and school provisional | partial, low |
| [F-8bin](fragments/F-8bin) BnF, lat. 9377 ff. 90-93 | De sacramento eucharistiae | hexameter poem on the sacraments in dietae; no exact match located | not identified |
| [F-lmfj](fragments/F-lmfj) Oudenaarde, Hs. 20/5 | medical text with gloss | Hippocrates, De regimine acutorum II, with Galen's commentary (Articella) | identified, high |
| [F-o1p7](fragments/F-o1p7) Oudenaarde, BB 0027 | Roman law | Bernardus Compostellanus jr, Lectura on the Decretals, X 1.6.23-24 | identified, high |
| [F-8bfm](fragments/F-8bfm) Toruń, Ob.6.II.2164 | theological treatise | Robert Holcot, Super Sapientiam, lectio II-III | identified, high |
| [F-h8oz](fragments/F-h8oz) Oudenaarde, nr. 56 | canon law | close parallel to Durantis, Speculum II.3; relationship unresolved | partial, medium |
| [F-szxp](fragments/F-szxp) Leipzig, Fragm. lat. 52 | medical fragment | medical florilegium; Arnoldus Saxo candidate unverified | partial, medium |
| [F-072h](fragments/F-072h) Leuven, Ms. 1206 | medical treatise | Aphorisms VII commentary + provisionally identified Galenic chapter table | partial, medium |
| [F-b8xt](fragments/F-b8xt) Bruges, Fragm. 27 | philosophical text | Metaphysics VII questions drawing on Aquinas; author and school unresolved | partial, medium |
| [F-nxl7](fragments/F-nxl7) Bruges, Ms. 466 | treatise on physics | Parva naturalia questions; exact base text and author unresolved | partial, low |
| [F-0kql](fragments/F-0kql) Park Abbey, VIIIB20/51 | life of Gregory the Illuminator | Latin Gregory life in Agathangelos tradition; exact recension unresolved | partial, low |
| [F-hcpv](fragments/F-hcpv) Park Abbey, VIIIB20/52 | legend of Gregory the Illuminator | ending of Latin Gregory life; probable relationship to F-0kql | partial, low |
| [F-2a37](fragments/F-2a37) Locarno, MdS 38 Fa 31 | commentary on a religious text | worn to illegibility; needs UV or raking light | not identified |

The research was performed by Claude, with lead-LLM image spot-checks and a second-model review by Codex on 20 September 2026. This is not human palaeographic verification. Eight identifications are supported by sampled manuscript/edition comparisons; Bernardus was checked against edition OCR rather than printed page images. Cherubino remains a provisional parallel. The partial reports received an evidence audit, not a full fresh collation.

See [REVIEW.md](REVIEW.md) for the scope, evidence links, and remaining limits; [CONVENTIONS.md](CONVENTIONS.md) for status definitions; and [METHOD.md](METHOD.md) for the research process. Failure to find a text in the recorded searches does not establish that it is unprinted or a new witness.

## Working here

Start with [AGENTS.md](AGENTS.md). [METHOD.md](METHOD.md) is the short research
workflow and [CONVENTIONS.md](CONVENTIONS.md) defines the evidence standards.
Image/reading, HTR, and retrieval manuals are references for the task at hand,
not prerequisites to read or execute in full.

## Layout

```
data/fragments.json            one row per fragment: catalogue data, our result, confidence, links, thumbnail URL
data/unidentified-*.csv        the corpus list, from a sweep of Fragmentarium's search
fragments/<F-id>/README.md     transcription, comparison table, ruled-out list, open items
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

Identifications go to fragmentarium@unifr.ch with the holding library copied, in Fragmentarium's
own field names. Nothing has been sent yet as of 20 September 2026.
