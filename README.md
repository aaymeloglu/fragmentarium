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

## Results so far (20 September 2026: 22 fragments, 9 identified, 11 partial, 2 not identified)

| Fragment | Catalogued as | Result | Confidence |
|---|---|---|---|
| [F-ss0e](fragments/F-ss0e) Antwerp, Fragm. 237 | theological treatise, 11th c. | Cherubino da Spoleto, Sermones quadragesimales (leaf is 15th c.) | identified, high |
| [F-1exy](fragments/F-1exy) Toruń, Rps 65/V | Genesis commentary | Nicholas of Lyra, De differentia nostrae translationis ab hebraica littera, Genesis | identified, high |
| [F-2e1n](fragments/F-2e1n) Bruges, reeks 538 | Latin etymology | Johannes Balbus, Catholicon, letter C | identified, high |
| [F-cfry](fragments/F-cfry) Vienna, Cod. 4070 | homily | Nicholas of Lyra, Postilla on Hebrews 5 | identified, high |
| [F-eo5z](fragments/F-eo5z) Ghent, HS.2582/290 | natural philosophy | Richard of Middleton, Quaestio de gradu formarum | identified, high |
| [F-s8db](fragments/F-s8db) Park Abbey, IIIB1.429 | gloss on canon law | Guido de Baysio, Rosarium super Decreto, C.10 q.1 | identified, high |
| [F-jaob](fragments/F-jaob) BnF, lat. 9377 ff. 70-73 | Sentences IV commentary | anonymous abbreviatio of Lombard IV; verses ps.-Bonaventure, prose the summa Hus used | partial, medium |
| [F-3yl2](fragments/F-3yl2) Toruń, Ob.6.II.684-686 | treatise with Summa fragment | compendium reworking Aquinas ST IIa-IIae q.10-11 with law citations | partial, medium |
| [F-ahiy](fragments/F-ahiy) Bruges, Ms. 95/130 | encyclopaedia | alphabetical tabula of auctoritates, sources traced | partial, low |
| [F-nei7](fragments/F-nei7) Ghent, HS.2582/164 | metaphysics | Franciscan Sentences I question near d.20, unedited | partial, low |
| [F-8bin](fragments/F-8bin) BnF, lat. 9377 ff. 90-93 | De sacramento eucharistiae | hexameter poem on the sacraments in "dietae", unprinted | not identified |
| [F-lmfj](fragments/F-lmfj) Oudenaarde, Hs. 20/5 | medical text with gloss | Hippocrates, De regimine acutorum II, with Galen's commentary (Articella) | identified, high |
| [F-o1p7](fragments/F-o1p7) Oudenaarde, BB 0027 | Roman law | Bernardus Compostellanus jr, Lectura on the Decretals, X 1.6.23-24 | identified, high |
| [F-8bfm](fragments/F-8bfm) Toruń, Ob.6.II.2164 | theological treatise | Robert Holcot, Super Sapientiam, lectio II-III | identified, high |
| [F-h8oz](fragments/F-h8oz) Oudenaarde, nr. 56 | canon law | contains Durantis, Speculum iudiciale II.3 verbatim; rest unprinted (recension or source) | partial, medium |
| [F-szxp](fragments/F-szxp) Leipzig, Fragm. lat. 52 | medical fragment | medical florilegium on sleep in Arnoldus Saxo's manner; likely his unedited Practica | partial, medium |
| [F-072h](fragments/F-072h) Leuven, Ms. 1206 | medical treatise | anonymous commentary on Aphorisms VII + chapter table of Latin Galen | partial, medium |
| [F-b8xt](fragments/F-b8xt) Bruges, Fragm. 27 | philosophical text | quaestio commentary on Metaphysics VII quoting Aquinas; Versor the lead | partial, medium |
| [F-nxl7](fragments/F-nxl7) Bruges, Ms. 466 | treatise on physics | question commentary on De longitudine vitae / De morte et vita; Jandun the lead | partial, low |
| [F-0kql](fragments/F-0kql) Park Abbey, VIIIB20/51 | life of Gregory the Illuminator | Latin life abridged from Greek Agathangelos, recension not in the editions | partial, low |
| [F-hcpv](fragments/F-hcpv) Park Abbey, VIIIB20/52 | legend of Gregory the Illuminator | final section of the same life; same manuscript as F-0kql | partial, low |
| [F-2a37](fragments/F-2a37) Locarno, MdS 38 Fa 31 | commentary on a religious text | worn to illegibility; needs UV or raking light | not identified |

What the labels mean: [CONVENTIONS.md](CONVENTIONS.md). How the work is done, and in what order to
search: [METHOD.md](METHOD.md). The pattern after twenty-two: the much-printed works fall to Google Books plus one edition; the
compilations, indexes and school commentaries that never reached print get their sources pinned and
then need a manuscript catalogue or an incunable read by eye, not a search.

## Layout

```
data/fragments.json            one row per fragment: catalogue data, our result, confidence, links, thumbnail URL
data/unidentified-*.csv        the corpus list, from a sweep of Fragmentarium's search
fragments/<F-id>/README.md     transcription, comparison table, ruled-out list, open items
docs/                          the site; python3 docs/_build_site.py regenerates it (stdlib only)
tools/searchd.py               local search service: Google Books, archive.org full text, Corpus Corporum on localhost (holds the key)
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
