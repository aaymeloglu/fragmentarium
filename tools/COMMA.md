# Searching manuscripts with CoMMA

`comma.py` searches [CoMMA](https://huggingface.co/datasets/comma-project/comma-jsonl)
(Clérice, Gabay, Vlachou-Efsthatiou, Pinche and Sagot,
[LREC 2026](https://aclanthology.org/2026.lrec-1.560/); CC-BY 4.0). CoMMA is
machine-read text (Kraken with CATMuS models) of about 32,800 digitised
manuscripts in Latin and Old French, harvested over IIIF, mostly from French
municipal libraries, the BnF, the Bodleian and e-codices. Every other source in
[RETRIEVAL.md](../RETRIEVAL.md) searches printed editions. CoMMA searches
manuscripts, so it can find a text that was never printed: an anonymous
commentary, an apparatus, a sermon cycle, or a compilation known only in copies.

## Installing

The corpus is 26.8 GB in seven parts and is kept outside the repository, in
`~/.cache/fragmentarium/comma` (or `$FRAGMENTARIUM_COMMA_DIR`, or `--dir`). It
is installed only when the person running the checkout agrees to the download:

```sh
uv run python tools/comma.py status            # absent, declined, incomplete, partial or installed
uv run python tools/comma.py fetch --yes       # all seven parts, then index (needs ~27 GB free)
uv run python tools/comma.py fetch --parts 6 --yes   # one 2.1 GB part, for a trial
uv run python tools/comma.py decline           # remember a "no" so setup does not ask again
```

`fetch` downloads a pinned dataset revision, resumes interrupted parts, and
checks each part's size and sha256 before using it. A part that fails the check
is deleted. It then indexes the shelfmarks and samples word frequencies, which
takes about a minute. Rerunning `fetch` is safe: parts already present are
re-hashed and skipped. A partial install searches only the parts present, and
the result names them.

## Searching

Give passages in reading order, expanded, in the reading's spelling. Break a
passage at every gap, illegible stretch or change of face; never join across a
gap. On the command line:

```sh
uv run python tools/comma.py search --fragment F-h8oz \
  --passage 'sed pone quod apparet auditorem impetratum esse sed non' \
  --passage 'constat per principalem an per procuratorem fuit obtentus' \
  --passage 'ad cuius instanciam sit datus auditor'
```

Or a JSON file of one object or a list. `usable: false` records are skipped, and
other fields such as `ref` and `basis` are carried along for your own records:

```json
[{"fragment": "F-h8oz",
  "passages": [{"text": "sed pone quod apparet auditorem impetratum esse sed non",
                "ref": "1v a 2-3", "basis": "image-only batch-2026-10-12-image-only"}]}]
```

```sh
uv run python tools/comma.py search queries.json --json > result.json
```

One pass reads the whole corpus however many queries it carries, so batch the
queries. On an 18-core laptop a pass took 14 minutes for 36 queries and 17 for
164. Each query is run alongside a shuffled copy, so these are 72 and 328
searches.

## How matching works, and what the numbers mean

The HTR text keeps abbreviation signs unexpanded (`ꝑ`, `ꝓ`, a tilde over a
vowel) and has roughly 10% character errors. After folding `v`/`u`, `j`/`i` and
the MUFI letter signs, a corpus word matches a query word:

- exactly (weight 1.0), or exactly but carrying an abbreviation sign (0.9);
- at one inserted, missing or wrong letter, for query words of six letters or
  more (0.8);
- when it carries an abbreviation sign, as a prefix of three or more letters of
  the query word: `auditorẽ` for *auditorem* (0.6).

Very frequent words (more than 5 per 100,000 corpus tokens) and a short Latin
stoplist are not searched. Each match is weighted by the word's rarity. A hit
is the best-scoring chain of matches within 150 tokens whose query positions
increase, so the words must come in the fragment's order.

Each query is also run with its own words shuffled. **margin** is the hit's
score minus the best shuffled score, and is the number to rank by. The raw score
mostly measures how many rare words the query has. In the
[blind controls](../audits/comma-controls-2026-10-20.md), every hit with a
margin of 3 or more was real textual agreement. But only about half of those
were the fragment's work. The others were a source it quotes, the Bible verse
it quotes, or the base text it comments on. Hits under 2 were mostly chance.

## Using a hit

A hit is a lead, as in [CONVENTIONS.md](../CONVENTIONS.md): collate before you
rely on it.

```sh
uv run python tools/comma.py context 'Reims. Bibliothèque de Reims, Ms. 708' 684978
uv run python tools/comma.py context 'Reims. Bibliothèque de Reims, Ms. 708' --find 'hyspano'
```

`context` prints the text around an offset, the IIIF manifest, the page count
and the library's scope note. CoMMA text carries no page breaks, so
`position x pages` only estimates the canvas. Find the page in the manifest and
read the image before citing a folio. Read several thousand characters around
the hit and collate line by line. Before deciding what the hit shows, ask:

- **Is it the base text?** Commentaries and glosses quote their lemmata, and a
  sermon quotes its pericope. A manuscript of the base text (the Bible, the
  Institutes, the Doctrinale, Priscian) matches the quoted words and nothing of
  the commentary.
- **Is it text already identified?** A further witness of the part the ledger
  already has is not a new identification, though it can still be useful (a
  closer recension, a French witness).
- **Is it a commonplace?** Standard prayers, computus formulas and
  mnemonic verses recur everywhere.
- **Does it reach the unresolved text?** A new identification needs sustained
  agreement in that text over several lines, beyond any verse or formula.
  Quote both sides.

Then identify the CoMMA manuscript's work from its catalogue (the scope note,
Biblissima, BnF Archives et manuscrits, IRHT/ARCA) and cite the manuscript by
its current shelfmark. CoMMA labels can be old numbers: its "Arras, Ms. 508" is
CGM 508, now Ms. 590.

## Limits

- Coverage is what CoMMA harvested: mostly French collections; German,
  Austrian, Italian and Dutch libraries are thin, and charters are rare. A miss
  is not an exclusion.
- Recognition is worse for cursive, Beneventan and faint text. Segmentation
  errors (skewed lines, marginalia merged into the text) break word order
  locally.
- Old French is included but untested here. Middle Dutch and German are not in
  the corpus, so Dutch hits are chance matches on function words.
- Short or broken readings do poorly. Queries with fewer than about ten
  searchable words seldom separate from the shuffled baseline. The baseline
  can also hit the true source, because a few shuffled words still form a
  short chain in it: Psalm 1 queried with seven searchable words finds Psalters
  at a margin under 2. For a short query, a low margin is not evidence against
  a hit. Read it anyway.
