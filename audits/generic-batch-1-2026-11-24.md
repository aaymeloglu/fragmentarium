# Records titled only by kind of text, first batch, November 2026

The first batch drawn from the whole-catalogue sweep for records whose title
names only a kind of text ("sermons", "commentary", "legal text"; scope
`generic` in `tools/sweep.py`). Twenty records were chosen from 139 surveyed
for continuous legible text with searchable wording. Eight are identified,
nine partial and three unidentified.

| Record | Result |
|---|---|
| F-reyc | Identified: Dinus de Mugello, commentary on the regulae iuris of the Liber Sextus, regulae 20-21 and 30-32 |
| F-5552 | Identified: Johannes de Imola on the Decretals, X 3.17.6 (Cum causa); catalogued as Roman law |
| F-zms8 | Identified: Hostiensis, Summa aurea III, end of De decimis and opening of De regularibus |
| F-r5u2 | Identified: Guido de Baysio, Rosarium super Decreto, De consecratione D. 2-3 |
| F-5wen | Identified: Hugh of Saint-Cher, Postilla super Ieremiam, Jer 49-51 |
| F-gcgt | Identified: the Termini naturales as printed in the Oxford Libellus sophistarum (1510); version open |
| F-kzqr | Identified: John Buridan, Summulae de dialectica VII, 7.4.3, against Hubien's transcription |
| F-4tsf | Identified: Nicholas Trevet, commentary on De civitate Dei III.17-30, against BnF Latin 2075; catalogued as a history |
| F-xd3f | Partial, medium: literal Peri hermeneias commentary ascribed to Siger of Courtrai (Erfurt CA 2° 135 has it under Thomas); redaction open |
| F-xmi2 | Partial, medium: lecture commentary on the glossed Ezekiel, close to Stephen Langton (Brugge 38) but not the same text |
| F-deal | Partial, medium: the sermon on Io 6:44 with the procession of sinners also in Eichstätt st 447 and Nürnberg Cent. IV 82; incipits only |
| F-23p7 | Partial, medium: a seven-thunders Judgment sermon related to Herolt, Sermo V, with sin speeches as in Peregrinus of Opole |
| F-uupq | Partial, medium: sermon and question notebooks; Frag. 3r excerpts Aquinas, Super Sent. IV d. 50 and d. 45 |
| F-0qke | Partial, medium: a preachers' key-word compilation abridging Peraldus, Summa de virtutibus |
| F-351r | Partial, low: a modistic question-commentary on Donatus; one question parallels an opinion reported by Radulphus Brito |
| F-q66i | Partial, low: decretist quaestiones disputatae ("thema ... queritur an possit"); collection not found |
| F-rx24 | Partial, low: Latin sermons, including one on St Bernard |
| F-s7q4 | Unidentified: German Ascension and Christmas sermons |
| F-ghq7 | Unidentified: a sermon to nuns on the wise virgins' oil; the flesh side newly read |
| F-v6la | Unidentified: Marian sermons, ff. 60-63; two incipits listed in the Zwettl and Basel catalogues, unread |

## Process

1. Twenty isolated readers (Claude Opus 5.5) read the tiled images with no
   catalogue or search access. The machine running the batch crashed during
   reading; the thirteen unfinished response files were recovered verbatim
   from the readers' transcripts and finished by a second isolated reader per
   packet, given the first reader's text and a hand-off naming tiles only.
   The packets were rebuilt from the spec with identical numbering. The first
   readings were frozen before research (`generic1-2026-11-24-image-only`).
2. Research by ten sessions (Claude Fable 5.2), two records each.
3. For each identification the coordinator read one matched passage on the
   manuscript image against the source (page images for seven; Hubien's
   transcription for F-kzqr).
4. Two blind readers (Claude Opus 5.5) transcribed 41 renamed, shuffled crops
   with no transcription or source. They confirmed the content of every
   identification. They corrected or withdrew readings made with a source in
   hand: F-deal's division reads "iudicium futurum, mors et infernus", not the
   devil supplied from the Eichstätt incipit; F-s7q4's thema reads "in
   nubibus", not "iubilo"; F-reyc's catchword is not the catalogue's "impetere
   prohibetur"; F-5552's running title reads "de emptor[e] et vendi[tore]";
   F-uupq's "virga" and F-rx24's "descendit de palacio" are not supported; the
   year numerals and proper names on F-4tsf 1r and 6r stay uncertain. The
   coordinator read F-reyc's "actione vendi(ti)" (print: "redhibitoria") and
   F-23p7's "maledicta auaricia" on the images.

## Unavailable sources

- The Munich full-text search (`tools/mdzsearch.py`) returned an HTML error
  page to every query throughout; the printed Donatus commentaries and some
  sermon prints were therefore not searched. The Munich image server worked.
- HathiTrust refused plain requests; Erfurt images needed the browser.
- e-codices reset connections late in the batch; the image links in the F-4tsf
  report follow the address pattern of the images acquired earlier but were
  not opened after writing.
- Several outside sources (Verhaak's edition of Siger, Venice Marc. lat. VI 21,
  Kaeppeli's Scriptores, Fransen's repertory of quaestiones, Schneyer vols.
  2-3) were not reached.

These are recorded as untested, not as negative results.
