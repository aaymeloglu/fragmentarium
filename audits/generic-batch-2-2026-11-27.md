# Records titled only by kind of text, second batch, November 2026

The second batch drawn from the whole-catalogue sweep for records whose title
names only a kind of text (scope `generic` in `tools/sweep.py`). Twelve records
came from the screening of the first batch (its reserves and the next-ranked
records); eight were screened from the open generic rows not looked at before.
Nine are identified, eight partial and three unidentified.

| Record | Result |
|---|---|
| F-0p2y | Identified: *Liber novem iudicum*, questions of the fourth house (land, houses, inheritances, hidden treasure), with the opening of Alkindus on treasure; catalogued as astrological and juridical |
| F-3gzf | Identified: *Digestum vetus* D. 15.1.4-11 (De peculio) with the Accursian gloss |
| F-cd6b | Identified: the apparatus of glosses on Raymond of Peñafort, *Summa de casibus* III, ascribed to William of Rennes (printed 1603 as glosses of Johannes de Friburgo); catalogued as a gloss on the Decretals |
| F-k6l1 | Identified: the treatise *De accentibus* as transmitted in Johannes Marchesinus, *Mammotrectus* |
| F-t2ia | Identified: Jordanus de Nemore (ascribed), *Demonstratio de algorismo*, Eneström defs. 1-13, omitting 4 and breaking off in 13; catalogued as a treatise on cubes and circles |
| F-utlg | Identified: Alexander de Villa Dei, *Doctrinale* ch. 8-9, with the Glosa "Admirantes" as in BnF lat. 8422 |
| F-wur7 | Identified: Guido de Baysio, *Apparatus ad Sextum*, VI 1 (De aetate et qualitate, De filiis presbyterorum) |
| F-xra7 | Identified: "Guillermus", *Postilla super epistolas et evangelia*, Gospel postil for Dominica XIX post octavas Pentecostes (the nineteenth Sunday after the octave of Pentecost), in a shorter form than the Ulm print |
| F-yxvr | Identified: Papias, *Elementarium*, letter F, Facio-Favilla |
| F-32dj | Partial, medium: a commentary on the *Doctrinale* at the opening of Part II, with an added extract from Richard of St Victor on the Apocalypse |
| F-3atu | Partial, medium: an expanded Middle Dutch parallel to reasons four and five of Sermo 57 of the *Sermones Thesauri novi de tempore*; containing sermon open |
| F-cr5h | Partial, medium: a commentary on the *Graecismus* IX-X; commentary unidentified |
| F-vva3 | Partial, medium: a commentary on the *Graecismus*, probably the same as F-cr5h, end of IX and X; how the two bifolia nest is not proven |
| F-exbj | Partial, medium: an accessus to Ovid's *Metamorphoses* with a prose summary of Book I; catalogued as a treatise on creation |
| F-kh5n | Partial, medium: a German exposition of Isaiah 53:8-12 closely paralleling Aquinas, *Super Isaiam* 53 (immediate source unresolved); containing work unidentified |
| F-2ees | Partial, low: a twelfth-century question treatise on syntax in the Priscianus minor tradition |
| F-a5ev | Partial, low: two sermons for St Lawrence; searches for these phrases returned p. 157 of Ziegler's description of Zwettl Cod. 348 (no text seen) |
| F-7fxt | Unidentified: a commentary on the *Doctrinale*, locus not established |
| F-g7bj | Unidentified: a question-commentary on Donatus, *Ars minor* |
| F-w647 | Unidentified: a school gloss on Petrus Hispanus, *Tractatus* III-IV |

## Process

1. Twenty isolated readers (Claude Opus 5.5), one per packet, read the tiled
   images with no catalogue or search access. Two readers (packets 01 and 06)
   were sent back to read named tiles again at native size; the packet-01
   reader consulted an advisor model about process only, as its response
   states. The first readings were frozen before research
   (`generic2-2026-11-27-image-only`).
2. Research by ten sessions (Claude Fable 5.2), two records each. A usage
   limit stopped all ten; fourteen reports had been written. Four sessions
   (Claude Opus 5.5) finished the remaining six records from the saved crops,
   rereading what they relied on.
3. For each identification the coordinator read one matched passage on the
   manuscript image against the source's page image (Eneström for F-t2ia, the
   Ulm print for F-xra7, BnF lat. 8422 for F-utlg, the Venice 1509 print for
   F-0p2y, the Milan 1490 print for F-wur7, the Rome 1603 print for F-cd6b,
   BnF lat. 7609 for F-yxvr, BnF lat. 1803 for F-k6l1) or, for F-3gzf, against
   a transcription of the Digest.
4. Two blind readers (Claude Opus 5.5) transcribed 59 renamed, shuffled crops
   from nineteen records with no transcription or source. Where they disagreed
   with a research reading the coordinator reread the crop. Results: F-2ees's
   heading "De exigentia participiorum" stands (the blind readers misexpanded
   the abbreviation); F-t2ia's top line reads "ascendit(ur)", not
   "accenditur"; F-exbj's first word is not settled; F-7fxt's display lemmata
   are not secure, so its locus is withdrawn; the openings of two F-wur7 lines
   read with the print in hand were withdrawn from the comparison; F-cd6b's lemma is
   "engel[tru]dam(?)"; F-kh5n's last word is not "ewang-"; the F-vva3/F-cr5h
   seam and the F-a5ev seam words are unconfirmed. The reports and ledger
   notes carry these as uncertain.

## Unavailable sources

- The Leipzig image server (iiif.ub.uni-leipzig.de) did not answer on
  27 November 2026, also through a foreign exit. Six Leipzig records chosen
  in the first screening (F-zuvw, F-xfhm, F-hd4j, F-twri, F-ucw4, F-redb) were
  therefore left for a later batch.
- The Munich full-text search (`tools/mdzsearch.py`) failed throughout.
- Zwettl, Cod. 348 is not digitised; Graz UB 1503 is lost; Busard's edition of
  the *Demonstratio* was seen only in text excerpts, and Ziegler's Zwettl
  catalogue only as page hits for searched phrases; the Leonine text of Aquinas on Isaiah was seen only as the Corpus
  Thomisticum transcription.

These are recorded as untested, not as negative results.

## Review

Codex (GPT) reviewed the pull request on 28 November 2026. It agreed with all
nine identifications and with the statuses and confidence levels of all twenty
records. Its corrections were applied to the reports and ledger. The
substantive ones: F-t2ia reads "fiant" with Eneström, which withdraws a variant
("fiunt") that the coordinator had accepted with the report in hand; the
attributions in the `persons` fields of F-k6l1, F-cd6b, F-xra7, F-0p2y and
F-t2ia (the *De speculis* lines) are qualified; the F-utlg estimate of one lost
bifolium is withdrawn in favour of the verse gap; the statements of source
coverage for F-0p2y, F-3gzf and F-yxvr are corrected; and the F-a5ev lead is
restated as search hits.

## Redaction of local paths

Twelve of the first readers' responses (packets 01, 04, 05, 06, 08, 10, 12, 14,
15, 17, 18 and 20) mentioned the local paths of crops they made. Before
publication, on 28 November 2026, each such path was reduced to its file name
and the twelve image-only readings were frozen again from the redacted text; no
reading, line or word was otherwise changed. The `reader` field of each says
so. The source-assisted readings of F-0p2y, F-3gzf, F-t2ia and F-k6l1, which
record the checksum of their first reading, were saved again unchanged against
the new checksums. The unredacted responses are kept outside the repository.
