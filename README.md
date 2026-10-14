# Fragmentarium: identifying the unidentified

[Fragmentarium](https://fragmentarium.ms/) is the international database of medieval manuscript
fragments, the leaves and strips cut from old books and reused as binding waste. <!-- corpus:start -->
The latest sweep of its search (2026-10-14, `tools/sweep.py`) found 363 records whose title or
summary calls the text unidentified or unknown, in English or another language
([corpus list](data/unidentified-2026-10-14.csv)); with records worked from earlier sweeps, the corpus is 364.
<!-- corpus:end -->
This repository works through them: read the fragment from
the library's images, find the text in a printed edition or a digital corpus, and write the
comparison out so anyone can check it.

The [results table with thumbnails](https://aaymeloglu.github.io/fragmentarium/) publishes
supported identifications, with a sortable date of identification and links to the evidence.
Only results recorded as identified with high confidence are published. Unresolved attempts
stay in the [research ledger](data/fragments.json); they do not require public writeups.
The [research progress page](https://aaymeloglu.github.io/fragmentarium/burndown.html) tracks the
corpus, distinguishing examined but unresolved fragments from unexamined ones.

## Identifications

<!-- identifications:start -->
225 fragments examined; 51 identifications published.

| Fragment | Identification | Date identified |
|---|---|---|
| [F-yybk](https://aaymeloglu.github.io/fragmentarium/F-yybk.html) | Johannes Dacus, De gradibus formarum (sophisma), ed. Otto 1955, pp. 554-555 and 561 | 2026-10-14 |
| [F-mgx2](https://aaymeloglu.github.io/fragmentarium/F-mgx2.html) | Gilbert the Universal, Glossa ordinaria in Lamentationes, book I, on Lam. 1:16 and 1:17 | 2026-10-14 |
| [F-rjkx](https://aaymeloglu.github.io/fragmentarium/F-rjkx.html) | Marcus, Visio Tnugdali (Vision of Tundale), Anglo-Norman translation in octosyllabic couplets, Lucifer to the field of joy (ed. Wagner 1882, pp. 36-41) | 2026-10-14 |
| [F-q5ti](https://aaymeloglu.github.io/fragmentarium/F-q5ti.html) | Anonymous preaching compilation of exempla in 20 chapters (prologue 'In hoc consequenti opusculo ordinantur in certis titulis'), section IV De sanctis, subchapters 1-6 and 34-39 (= Cambridge CCCC MS 327, ff. 175v-176r, 179v-180v) | 2026-10-14 |
| [F-kcu7](https://aaymeloglu.github.io/fragmentarium/F-kcu7.html) | Anonymous, Compilationes supra Summulas Petri Hispani ('Omnes homines'), divisio textus on Tracts IX-XI (de Rijk 1972 numbering); fuller redaction than the Nuremberg copy | 2026-10-14 |
| [F-nfu2](https://aaymeloglu.github.io/fragmentarium/F-nfu2.html) | Hippocrates, Regimen acutorum, book IV with Galen's commentary (Latin), Textus XIX-XX and XXIV-XXVII (Giunta 1527 numbering) | 2026-10-14 |
| [F-lodh](https://aaymeloglu.github.io/fragmentarium/F-lodh.html) | Liturgical psalter (Gallican), Psalm 68:15-22; probable Psalms 59, 61-62 and 67 on the other faces | 2026-10-13 |
| [F-ypxa](https://aaymeloglu.github.io/fragmentarium/F-ypxa.html) | Hostiensis (Henricus de Segusio), Lectura in Decretales Gregorii IX, on X 3.30.33-34 (De decimis: end of c. Cum non sit in homine, and c. Nuper abbates) | 2026-10-13 |
| [F-3l5z](https://aaymeloglu.github.io/fragmentarium/F-3l5z.html) | Geert Grote, Getijdenboek (Middle Dutch hours), Hours of the Eternal Wisdom, Compline: end of hymn Ihesus regniert in den vreden and antiphon O gloriose coninc onder dinen heilighen (Van Wijk 1940, p. 111) | 2026-10-13 |
| [F-ne56](https://aaymeloglu.github.io/fragmentarium/F-ne56.html) | Missal, Holy Week: Tuesday, end of the Passion according to Mark (15:43-46); Wednesday, lesson Isaiah 63:5, 7 and gradual Ne avertas (Ps 68:18, 2). Use not determined | 2026-10-13 |
| [F-x6c5](https://aaymeloglu.github.io/fragmentarium/F-x6c5.html) | Psalter text, Psalm 49:5-10 (Gallican or Roman wording) on the strip in the "ant" images; the second strip probably Psalm 49:15-20. Kind of book open (psalter, breviary or Bible) | 2026-10-13 |
| [F-3wqe](https://aaymeloglu.github.io/fragmentarium/F-3wqe.html) | Eberhard of Béthune, Graecismus, XIX 118-121 (lower strip, Frammento 3, only; upper strip unidentified) | 2026-10-13 |
| [F-cckq](https://aaymeloglu.github.io/fragmentarium/F-cckq.html) | Tabula utriusque iuris attributed to Johannes de Erfordia, article Appellatio (on tacit renunciation of an appeal) | 2026-10-12 |
| [F-bcte](https://aaymeloglu.github.io/fragmentarium/F-bcte.html) | Bede, De temporum ratione, chapter 43 (fol. F) | 2026-10-12 |
| [F-7nce](https://aaymeloglu.github.io/fragmentarium/F-7nce.html) | Aldobrandinus de Toscanella, Scala fidei (sermons on the Apostles' Creed): Tertia die resurrexit and Sedet ad dexteram | 2026-10-12 |
| [F-szlk](https://aaymeloglu.github.io/fragmentarium/F-szlk.html) | Servasanctus de Faventia, Antidotarius animae: the castle of the soul, chapters on feast days, on restraining touch and on the sixth gate | 2026-10-12 |
| [F-03xq](https://aaymeloglu.github.io/fragmentarium/F-03xq.html) | John of Abbeville, sermons for saints' days: Sicut exaltavit Moyses serpentem and Ego quasi vitis (Nativity of the Virgin) | 2026-10-12 |
| [F-kr2n](https://aaymeloglu.github.io/fragmentarium/F-kr2n.html) | Pseudo-Haymo, Liverani homiliary (anonymous Carolingian reworking of Haymo of Auxerre): homilies on Mark 8:1-9 (Barré 55, Liverani XLII), Matthew 7:15-21 (Barré 56, Liverani XLIV, end) and Luke 16:1-9 (Barré 57, Liverani XLV, start) | 2026-10-12 |
| [F-1szi](https://aaymeloglu.github.io/fragmentarium/F-1szi.html) | Pseudo-Haymo, Liverani homiliary (anonymous Carolingian reworking of Haymo of Auxerre): homily on Matthew 6:24-33 (Barré 67, Liverani LIII), ravens and lilies | 2026-10-12 |
| [F-vpe8](https://aaymeloglu.github.io/fragmentarium/F-vpe8.html) | Pseudo-Haymo, Liverani homiliary (anonymous Carolingian reworking of Haymo of Auxerre): homilies on Luke 7:11-16 (Barré 68, Liverani LIV, end) and Luke 14:1-11 (Barré 69, Liverani LV, start) | 2026-10-12 |
| [F-4usd](https://aaymeloglu.github.io/fragmentarium/F-4usd.html) | Pseudo-Galen, Liber de dynamidiis (Juntine 'Liber alter de dynamidiis'): De catharticis to De opio (f. 104) and recipes Contra vitia faciei to Electuarium dianthu (f. 105) | 2026-10-12 |
| [F-ziuq](https://aaymeloglu.github.io/fragmentarium/F-ziuq.html) | Henricus de Piro, Super Institutiones, on Inst. 1.7-1.8 and 1.21-1.24 | 2026-10-12 |
| [F-eflq](https://aaymeloglu.github.io/fragmentarium/F-eflq.html) | Johannes Versor, Quaestiones super libros Posteriorum Aristotelis, book II qq. 1, 2, 8 (reworded against the Cologne prints) | 2026-10-12 |
| [F-x61h](https://aaymeloglu.github.io/fragmentarium/F-x61h.html) | Cibaldone (anonymous Italian verse regimen, "Libro terzo dello Almansore"), end of the chapter on bathing, fol. 38r col. a | 2026-10-12 |
| [F-v0qx](https://aaymeloglu.github.io/fragmentarium/F-v0qx.html) | Johannes Matthaeus, Concionum dispositiones (Wittenberg, 1581; 2nd ed. 1590), end of the outline "De templorum dedicatione" (handwritten copy of pp. 865-868) | 2026-10-12 |
| [F-ja1n](https://aaymeloglu.github.io/fragmentarium/F-ja1n.html) | Johannes Faventinus, Summa super Decretum Gratiani, pars I, D. 86 (comment on c. 8 Qui venatoribus to c. 24 Tanta nequitia) | 2026-10-12 |
| [F-x60p](https://aaymeloglu.github.io/fragmentarium/F-x60p.html) | Justinian, Digestum vetus with the Accursian Glossa ordinaria, Digest 4.8.42-49 and 4.8.52-4.9.3 pr. (five of six strips placed, in one leaf) | 2026-10-12 |
| [F-cjzj](https://aaymeloglu.github.io/fragmentarium/F-cjzj.html) | Accursius, Glossa ordinaria on the Authenticum, Collatio IX: end of Ut iudices non expectent sacras iussiones (Nov. 125) and rubric to c. 1 of Ut litigantes iurent in exordio litis (Nov. 124); gloss only | 2026-10-12 |
| [F-w36h](https://aaymeloglu.github.io/fragmentarium/F-w36h.html) | Jacobus de Voragine, Legenda aurea, Southern Middle Dutch translation of c. 1357 attributed to Petrus Naghel (Gulden legende), chapter on the dedication of a church (Vander wiinghen der kerken): end of the canonical hours to the seven sprinklings of the altar | 2026-10-12 |
| [F-n8nv](https://aaymeloglu.github.io/fragmentarium/F-n8nv.html) | (Pseudo-)Hugh of St Victor, Expositio in regulam sancti Augustini, Middle Dutch translation with the lemmata of the Rule, chapters 6-7 (PL 176, cols 899-904) | 2026-10-12 |
| [F-t273](https://aaymeloglu.github.io/fragmentarium/F-t273.html) | Caesarius of Arles, Sermo 144 (ed. Morin), In letaniis, De agenda paenitentia et Ninevitis, complete (inc. Evangelica lectio fratres carissimi dum legeretur); the sermon between the catalogue's Maximus and Gregory texts | 2026-10-12 |
| [F-n5r2](https://aaymeloglu.github.io/fragmentarium/F-n5r2.html) | Bible, Canticle of Moses (Audite caeli), Deuteronomy 32:1-27, Vulgate; book type (psalter with canticles, breviary or Bible) not established | 2026-10-12 |
| [F-a07w](https://aaymeloglu.github.io/fragmentarium/F-a07w.html) | Aegidius de Fuscarariis, Ordo iudiciarius, cc. LXIX (Conclusio causae, second half) - LXX (Forma sententiae diffinitivae, opening); ed. Wahrmund pp. 124-126 | 2026-10-12 |
| [F-xukl](https://aaymeloglu.github.io/fragmentarium/F-xukl.html) | Psalms 149:1-4 and 149:8-150:3 in Geert Grote's Middle Dutch translation (as in his Getijdenboek, ed. Van Wijk 1940, pp. 46-47), on each of two leaves; probably a book of hours, kind of book and unity of the leaves not established | 2026-10-12 |
| [F-33ow](https://aaymeloglu.github.io/fragmentarium/F-33ow.html) | Gregorian sacramentary, Advent orations: Suscipiamus, Excita ... saluari, the six 'Aliae orationes de adventu' (Excita ... operare, Conscientias, Prope esto, Concede ... ut magnae, Mentes nostras, Preces populi tui), Porrige nobis, Deus qui nos conspicis; kind of book open | 2026-10-12 |
| [F-1kdv](https://aaymeloglu.github.io/fragmentarium/F-1kdv.html) | Justinian, Codex 7.62.31-32 (De appellationibus), with marginal gloss; second strip probably C. 7.65.8 | 2026-10-12 |
| [F-18n8](https://aaymeloglu.github.io/fragmentarium/F-18n8.html) | Accursius, Glossa ordinaria on the Digestum vetus, gloss "illatae sunt" to D. 4.9.1.8 (strip 1) | 2026-10-12 |
| [F-qycu](https://aaymeloglu.github.io/fragmentarium/F-qycu.html) | Avicenna, Canon medicinae (Latin of Gerard of Cremona), III, fen 3, tract. 1, end of ch. 1 (De anatomia oculi) and rubric of ch. 2 | 2026-10-12 |
| [F-su3k](https://aaymeloglu.github.io/fragmentarium/F-su3k.html) | Pharetra doctorum et philosophorum, section De amore inimicorum | 2026-10-11 |
| [F-rl44](https://aaymeloglu.github.io/fragmentarium/F-rl44.html) | Johannes Serapion the Elder, Breviarium medicinae, tract VII, chapter XX; upper-cover leaf | 2026-10-11 |
| [F-z56d](https://aaymeloglu.github.io/fragmentarium/F-z56d.html) | Petrus Hispanus (non-papa), Summa "Absoluta cuiuslibet" (grammar): on devocatio and on ille as demonstrative or relative | 2026-10-11 |
| [F-au0s](https://aaymeloglu.github.io/fragmentarium/F-au0s.html) | Bernard of Parma, Casus longi super Decretales, book III: casus on X 3.4.11–12 and X 3.5.5–6 | 2026-10-11 |
| [F-rygw](https://aaymeloglu.github.io/fragmentarium/F-rygw.html) | Galen, De sanitate tuenda (medieval Latin De regimine sanitatis), book VI, translation attributed to Burgundio of Pisa. | 2026-10-11 |
| [F-1exy](https://aaymeloglu.github.io/fragmentarium/F-1exy.html) | Nicholas of Lyra, Tractatus de differentia nostrae translationis ab hebraica littera, Genesis section | 2026-09-20 |
| [F-2e1n](https://aaymeloglu.github.io/fragmentarium/F-2e1n.html) | Johannes Balbus, Catholicon, letter C | 2026-09-20 |
| [F-cfry](https://aaymeloglu.github.io/fragmentarium/F-cfry.html) | Nicholas of Lyra, Postilla litteralis super Epistolam ad Hebraeos, chapter 5 | 2026-09-20 |
| [F-eo5z](https://aaymeloglu.github.io/fragmentarium/F-eo5z.html) | Richard of Middleton, Quaestio disputata de gradu formarum; leprous-parent and asses arguments | 2026-09-20 |
| [F-s8db](https://aaymeloglu.github.io/fragmentarium/F-s8db.html) | Guido de Baysio, Rosarium super Decreto, C.10 q.1 c.13 | 2026-09-20 |
| [F-lmfj](https://aaymeloglu.github.io/fragmentarium/F-lmfj.html) | Hippocrates, De regimine acutorum, with Galen commentary in the Latin Articella tradition | 2026-09-20 |
| [F-o1p7](https://aaymeloglu.github.io/fragmentarium/F-o1p7.html) | Bernardus Compostellanus iunior, Lectura in primum librum Decretalium, De electione | 2026-09-20 |
| [F-8bfm](https://aaymeloglu.github.io/fragmentarium/F-8bfm.html) | Robert Holcot, Super Sapientiam Salomonis, end of lectio II and part of lectio III | 2026-09-20 |
<!-- identifications:end -->

Dates record when the project first established the identification, not a later review or
site update; `examined` in the ledger records the latest examination.

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
The image, reading and search manuals are references for the task at hand,
not prerequisites to read or execute in full.

## Layout

```
data/fragments.json            attempt ledger: catalogue data, result, confidence, identified_on, examined, links
data/unidentified-*.csv        the corpus list, from tools/sweep.py (the latest file is current)
fragments/<F-id>/README.md     report required for published identifications; earlier research reports retained
prompts/                       the reading prompt and the briefs for reader, research and report sessions; prompts/README.md gives the batch sequence
docs/                          the site; python3 docs/_build_site.py regenerates it and this README's counts and table (stdlib only)
tools/searchd.py               local search service: Google Books, archive.org full text, Corpus Corporum on localhost (holds the key)
pyproject.toml + uv.lock       one Python 3.13 environment; optional `images` dependency group (Pillow)
tools/latin_search.py         tolerant Latin retrieval with original offsets and ordered passage ranking (optional; see tools/MATCHING.md)
tools/readings.py              neutral image packets, preserved first readings, separate source-assisted revisions
FIRST_READINGS.md             isolated-reader procedure and command examples
tools/iiif.py                  fetch a fragment's images: info, overview, tiles, crop; resolves each library's IIIF quirks
tools/ia_cluster.py            do the anchor phrases sit in one passage of an archive.org volume's OCR?
tools/gbwithin.py              search inside one Google Books volume: printed page number and snippet per hit, no key
tools/tilepacket.py            neutral reading packets of overview plus reading-size tiles from an acquire_batch cache
tools/schneyer.py              search Schneyer's sermon repertory volume by volume in archive.org full text
tools/hspsearch.py             search Handschriftenportal catalogue texts for an incipit, title or shelfmark; lists digital copies
tools/contactsheet.py          labelled thumbnails of every image in a record, for surveying before reading
tools/record.py                write results to the ledger; install an identification's report and assisted reading
tools/register.py              add unresearched fragments to the ledger from their cached manifests
tools/mdzsearch.py             full-text search of the Munich digital library's OCR (early printed books), no key
tools/survey.py                records not yet attempted: native image sizes, linked descriptions, ledger siblings, contact sheets for choosing a batch
tools/catalogue.py             what the catalogue already says: summary fields and the full description linked from the record page
tools/bnf.py                   pages of a BnF manuscript by shelfmark, for comparison (Gallica itself refuses scripts)
tools/mnlsearch.py             phrase search of the Corpus Middelnederlands (Middle Dutch), no key
tools/cantus.py                chant in Cantus Index and the Cantus Database: texts, concordances, runs of chants, manuscript readings
tools/sweep.py                 sweep Fragmentarium's search for records catalogued as unidentified; writes the corpus list
tests/                         data/folder/site consistency; CI fails if docs/ or this README is stale
```

No images are stored here. Thumbnails on the site are served by the holding libraries' IIIF
servers; rights stay with the institutions named on each record.

## Reporting

For catalogue submissions, use Fragmentarium's own field names and address fragmentarium@unifr.ch
with the holding library copied, as described in [CONVENTIONS.md](CONVENTIONS.md). Include the
relevant comparison and its limits; research runs do not send submissions automatically.
