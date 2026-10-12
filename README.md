# Fragmentarium: identifying the unidentified

[Fragmentarium](https://fragmentarium.ms/) is the international database of medieval manuscript
fragments, the leaves and strips cut from old books and reused as binding waste. A sweep on
20 September 2026 found 222 records with "unidentified" in the title or summary
([saved corpus list](data/unidentified-2026-09-20.csv)). This repository works through them: read the fragment from
the library's images, find the text in a printed edition or a digital corpus, and write the
comparison out so anyone can check it.

The [results table with thumbnails](https://aaymeloglu.github.io/fragmentarium/) publishes
supported identifications, with a sortable date of identification and links to the evidence.
Only results recorded as identified with high confidence are published. Unresolved attempts
stay in the [research ledger](data/fragments.json); they do not require public writeups.
The [research progress page](https://aaymeloglu.github.io/fragmentarium/burndown.html) tracks the
222-record corpus, distinguishing examined but unresolved fragments from unexamined ones.

## Identifications

62 fragments examined; 18 identifications published.

| Fragment | Identification | Date identified |
|---|---|---|
| [F-szlk](https://aaymeloglu.github.io/fragmentarium/F-szlk.html) | Servasanctus de Faventia, Antidotarius animae: the castle of the soul, chapters on feast days, on restraining touch and on the sixth gate | 2026-10-12 |
| [F-cckq](https://aaymeloglu.github.io/fragmentarium/F-cckq.html) | Tabula utriusque iuris attributed to Johannes de Erfordia, article Appellatio (on tacit renunciation of an appeal) | 2026-10-12 |
| [F-bcte](https://aaymeloglu.github.io/fragmentarium/F-bcte.html) | Bede, De temporum ratione, chapter 43 (fol. F) | 2026-10-12 |
| [F-7nce](https://aaymeloglu.github.io/fragmentarium/F-7nce.html) | Aldobrandinus de Toscanella, Scala fidei (sermons on the Apostles' Creed): Tertia die resurrexit and Sedet ad dexteram | 2026-10-12 |
| [F-03xq](https://aaymeloglu.github.io/fragmentarium/F-03xq.html) | John of Abbeville, sermons for saints' days: Sicut exaltavit Moyses serpentem and Ego quasi vitis (Nativity of the Virgin) | 2026-10-12 |
| [F-su3k](https://aaymeloglu.github.io/fragmentarium/F-su3k.html) | Pharetra doctorum et philosophorum, section De amore inimicorum | 2026-10-11 |
| [F-z56d](https://aaymeloglu.github.io/fragmentarium/F-z56d.html) | Petrus Hispanus (non-papa), Summa "Absoluta cuiuslibet", on devocatio and on ille as demonstrative or relative | 2026-10-11 |
| [F-au0s](https://aaymeloglu.github.io/fragmentarium/F-au0s.html) | Bernard of Parma, Casus longi on the Decretals, X 3.4.11–12 and X 3.5.5–6 | 2026-10-11 |
| [F-rl44](https://aaymeloglu.github.io/fragmentarium/F-rl44.html) | Serapion Senior, Breviarium, tract VII (antidotarium), chapter 20 | 2026-10-11 |
| [F-rygw](https://aaymeloglu.github.io/fragmentarium/F-rygw.html) | Galen, De regimine sanitatis, Book VI, medieval Latin translation | 2026-10-11 |
| [F-1exy](https://aaymeloglu.github.io/fragmentarium/F-1exy.html) | Nicholas of Lyra, Tractatus de differentia nostrae translationis ab hebraica littera, Genesis section | 2026-09-20 |
| [F-2e1n](https://aaymeloglu.github.io/fragmentarium/F-2e1n.html) | Johannes Balbus, Catholicon, letter C | 2026-09-20 |
| [F-cfry](https://aaymeloglu.github.io/fragmentarium/F-cfry.html) | Nicholas of Lyra, Postilla litteralis super Epistolam ad Hebraeos, chapter 5 | 2026-09-20 |
| [F-eo5z](https://aaymeloglu.github.io/fragmentarium/F-eo5z.html) | Richard of Middleton, Quaestio disputata de gradu formarum; leprous-parent and asses arguments | 2026-09-20 |
| [F-s8db](https://aaymeloglu.github.io/fragmentarium/F-s8db.html) | Guido de Baysio, Rosarium super Decreto, C.10 q.1 c.13 | 2026-09-20 |
| [F-lmfj](https://aaymeloglu.github.io/fragmentarium/F-lmfj.html) | Hippocrates, De regimine acutorum, with Galen commentary in the Latin Articella tradition | 2026-09-20 |
| [F-o1p7](https://aaymeloglu.github.io/fragmentarium/F-o1p7.html) | Bernardus Compostellanus iunior, Lectura in primum librum Decretalium, De electione | 2026-09-20 |
| [F-8bfm](https://aaymeloglu.github.io/fragmentarium/F-8bfm.html) | Robert Holcot, Super Sapientiam Salomonis, end of lectio II and part of lectio III | 2026-09-20 |

Dates record when the project first established the identification, not a later review or
site update. The eight original dates are supported by the original 20 September 2026 research commits
(`3c9d6db` and `6b7c316`). Two identifications come from the
[11 October batch](audits/batch-2026-10-11.md) and three more from a
[recheck of its unresolved records](audits/recheck-2026-10-11.md). `examined` separately records the latest examination.

Research and comparisons were performed by LLMs. The reports link selected manuscript passages
to printed sources and state the scope and limits of the evidence. Richard of Middleton was
compared with Hocedez's printed excerpts; the complete edition and apparatus remain unchecked.
Identification does not certify transcription accuracy or establish witness novelty.

See [CONVENTIONS.md](CONVENTIONS.md) for evidence standards and [METHOD.md](METHOD.md) for the
research process. The ledger retains all attempts, including source connections that do not
identify the containing work. Earlier reports and preserved readings remain in the repository
as research records. They are not additional published identifications.

## Working here

Start with [AGENTS.md](AGENTS.md). [METHOD.md](METHOD.md) is the short research
workflow and [CONVENTIONS.md](CONVENTIONS.md) defines the evidence standards.
Image/reading, HTR, and retrieval manuals are references for the task at hand,
not prerequisites to read or execute in full.

## Layout

```
data/fragments.json            attempt ledger: catalogue data, result, confidence, identified_on, examined, links
data/unidentified-*.csv        the corpus list, from a sweep of Fragmentarium's search
fragments/<F-id>/README.md     report required for published identifications; earlier research reports retained
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
tools/gbwithin.py              search inside one Google Books volume: printed page number and snippet per hit, no key
tools/tilepacket.py            neutral reading packets of overview plus reading-size tiles from an acquire_batch cache
tests/                         data/folder/site consistency; CI fails if docs/ is stale
```

No images are stored here. Thumbnails on the site are served by the holding libraries' IIIF
servers; rights stay with the institutions named on each record.

## Reporting

For catalogue submissions, use Fragmentarium's own field names and address fragmentarium@unifr.ch
with the holding library copied, as described in [CONVENTIONS.md](CONVENTIONS.md). Include the
relevant comparison and its limits; research runs do not send submissions automatically.
