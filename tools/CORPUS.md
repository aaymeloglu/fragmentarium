# A reusable homiletic corpus

`corpus_fetch.py` downloads the public OCR of twelve selected editions into the
existing checksummed corpus format. The collection covers homiliaries, sermons,
saints' lives and preaching aids: PL 39, 40, 76, 94, 95, 117, 131 and 165,
Graesse's *Legenda aurea*, both parts of Bromyard's *Summa praedicantium*, and
Petrus Hieremia's *Divinum opus*. The sources and pinned text checksums are in
[data/corpora/homiletic.json](../data/corpora/homiletic.json).

```sh
# List the sources without making network requests.
uv run python tools/corpus_fetch.py data/corpora/homiletic.json

# Fetch once; subsequent runs check and reuse cached bytes.
uv run python tools/corpus_fetch.py data/corpora/homiletic.json \
  --corpus scratch/homiletic/corpus.json

# Fetch only a particular source, or retry a failed download.
uv run python tools/corpus_fetch.py data/corpora/homiletic.json \
  --corpus scratch/homiletic/corpus.json --id bromyard-1

# Search ordered surviving spans using the existing matcher.
uv run python tools/latin_search.py --corpus scratch/homiletic/corpus.json \
  --query query.json --max-edits 1 --window 1800 --output results.json
```

Build `query.json` from the surviving reading using the [matching manual](MATCHING.md).
`parts` and bounded `gaps` describe separate surviving spans; alternative readings
stay explicit variants. `--ocr-long-s` can help with early prints whose OCR reads
long s as f, but increases false matches. The matcher processes the full OCR of
each volume; these are not snippet searches. A twelve-volume search can take a
few minutes and appreciable memory. There is no persistent search index.

The fetcher makes sequential requests, retries temporary transport failures and
records metadata, download addresses, byte counts, hashes and retrieval times in
`receipts/`. `fetch-results.json` records successes and failures for the latest
invocation. Any failed source makes the command exit nonzero; successful sources
remain usable. A missing, restricted, ambiguous or HTML response never enters the
corpus. A changed checksum stops that source rather than silently replacing it.
For a deliberately revised edition, use a new source id and checked checksum.

The collection is targeted, not comprehensive. Several PL texts can already be
phrase-searched in Corpus Corporum; downloading them adds ordered-gap and fuzzy
matching of damaged passages. The early printed preaching aids broaden the
reusable local coverage. Google Books and IA OCR can be poor, especially with
abbreviations, marginalia and two-column layouts. A no-hit result does not exclude
a work, and a source quotation does not identify the containing compilation.

## Adding editions and OCR

A collection entry names an IA item, an edition and its intended coverage; `file`
selects one `_djvu.txt` when an item has several. `sha256` pins reviewed source
bytes (omit only while checking a new source). This tool uses existing public OCR;
it does not install or run a new OCR engine or harvest library collections.

For a scanned edition without usable OCR, [Rescribe](https://rescribe.xyz/rescribe/)
can produce UTF-8 text from local page images or a PDF. Register its output with
the existing importer, giving it a distinct id from any earlier OCR:

```sh
uv run python tools/corpus.py --corpus scratch/homiletic/corpus.json \
  --id edition-reocr --text local-edition.txt \
  --source 'https://archive.org/details/ITEM' --edition 'Checked title and imprint'
```

Save the OCR engine/model/version, input-image hashes and page mapping alongside
the local corpus. The generic text importer preserves exact output bytes; it does
not independently certify those OCR settings. Neither imported OCR line numbers
nor form feeds establish printed page numbers. Inspect the linked scan before
citing wording or a locus. The collection's historical attribution labels are
finding aids, not endorsements of medieval or modern authorship.

Live acquisition and retrieval checks: [20 October audit](../audits/corpus-tooling-2026-10-20.md).
