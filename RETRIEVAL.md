# Where to search

Choose the source most likely to hold the text; this is not an order of work.
[METHOD.md](METHOD.md) says how to use a hit, and [CONVENTIONS.md](CONVENTIONS.md)
what it proves. Search distinctive connected prose of four to eight words. A hit
is a lead: read the page before relying on it.

| Source | Reach it with | Good for |
|---|---|---|
| Google Books | `searchd.py` `/gb?q=` (needs `GOOGLE_BOOKS_API_KEY` in the service's environment). `tools/gbwithin.py <volume id> '"phrase"'` then searches inside one volume and gives printed page numbers, with no key, also for snippet-view books in copyright. | Anything printed, above all after 1250. Snippets and volume ids, not page images. |
| Munich digital library (MDZ) | `tools/mdzsearch.py '"phrase" "phrase"'`, no key. | OCR full text of incunables and prints to about 1700; has found texts a Google Books phrase search missed. |
| Internet Archive | `searchd.py` `/ia?q=`. Google Books scans are often mirrored as `bub_gb_<volume id>`; a volume's OCR is at `archive.org/download/<id>/<id>_djvu.txt`. | Editions and repertories in full text. |
| Corpus Corporum | `searchd.py` `/cc?q=&index=p` (paragraph) or `index=s` (sentence); accepts `NEAR/N`. | Patrologia Latina and other early and high-medieval Latin. Thin for scholastic and late texts. |
| Corpus Middelnederlands | `tools/mnlsearch.py 'phrase'` (whole words; `.*` inside a word, `--cql` for gaps), no key. | About 370 Middle Dutch works in verse and prose. Spelling is not normalised; try variants. |
| Referenzkorpus Mittelhochdeutsch | Download the corpus (v2.1 is at zenodo.org/record/13982324) and search its normalised text locally; there is no phrase search to call. Handschriftencensus (handschriftencensus.de) lists German manuscripts and fragments by work. | Middle High German to about 1350; whether a German fragment is already recorded. |
| Sermon repertory | `tools/schneyer.py '"theme words"' '"word word word"~8'` searches Schneyer (1150-1350) volume by volume. | Sermon incipits. An incipit is a lead; compare the sermon body. |
| Manuscript catalogues | `tools/hspsearch.py '"incipit words"'` for German collections, with links to digitised copies; manuscripta.at for Austria; Biblissima and ARCA for France. | Unprinted works: find a digitised manuscript and collate. |
| BnF manuscripts | `tools/bnf.py 'Latin 15972' info`, then `overview`, `tiles` or `crop` with `--canvas N`. gallica.bnf.fr refuses scripts; this uses BnF's API host. | Reading a named Paris manuscript for comparison. No text search of Gallica's printed books. |
| Incunable copies | `tools/gw.py <GW number>` lists libraries holding a digitised copy. | Reading the page behind a snippet. |
| Liturgical chant | `tools/cantus.py text 'words'` gives Cantus IDs from standard texts (incipit, then anywhere in the text); `cid <id>` counts the feasts, services and genres of every manuscript in the Cantus Index network that has the chant; `next <id>` the chants that usually follow; `ms 'words'` searches Cantus Database manuscript readings in their own spelling. No key. | Antiphons, responsories, Mass chants, hymns and sequences: the feast, and whether the book served the Mass or the Office. Not readings, orations or sermons. |
| Subject sources | Corpus Thomisticum, Gloss-e, Friedberg's canon law, Analecta Hymnica, and the like, directly. | Their own fields. |

The search service is started once and shared:

```sh
GOOGLE_BOOKS_API_KEY=... uv run python tools/searchd.py   # listens on 127.0.0.1:8790
curl -s '127.0.0.1:8790/gb?q=%22phrase%20one%22%20%22phrase%20two%22'
```

It holds the key, caches results and spaces Google Books calls, so sessions that
use it need no credential. Google Books has a daily quota and fails
intermittently; when it does, use the other sources and say which searches were
not run.

Do not fetch books.google.com page or image addresses: bursts have triggered
captchas that also broke the search service. Treat a blocked or restricted
source as unavailable, not as a negative result.

For a reading too uncertain for a phrase search, or to compare one passage
across several downloaded texts, see [tools/MATCHING.md](tools/MATCHING.md).
