#!/usr/bin/env python3
"""Build the GitHub Pages site in docs/ from data/fragments.json and fragments/*/README.md.

Python 3, standard library only. From the repo root:

    python3 docs/_build_site.py

Writes docs/index.html (the table) and docs/<F-id>.html (one page per fragment, rendered from
the fragment folder's README). Images are never copied: thumbnails are hotlinked from the
holding library's IIIF server, as recorded in data/fragments.json.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPO = "https://github.com/aaymeloglu/fragmentarium"

STYLE = """
:root { --ink:#1f1b16; --muted:#6b6259; --accent:#8a3b12; --rule:#d9d0c3; --bg:#faf6ef; --surface:#fff; --serif:Georgia,'Times New Roman',serif; --mono:ui-monospace,Menlo,Consolas,monospace; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --ink:#e8e1d6; --muted:#a39b90; --accent:#e0956a; --rule:#3b352f; --bg:#171411; --surface:#1f1b17; } }
:root[data-theme="dark"] { --ink:#e8e1d6; --muted:#a39b90; --accent:#e0956a; --rule:#3b352f; --bg:#171411; --surface:#1f1b17; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font-family:var(--serif); font-size:17px; line-height:1.55; }
.wrap { max-width:1200px; margin:0 auto; padding:24px 16px 64px; }
h1 { font-size:34px; font-style:italic; color:var(--accent); margin:8px 0 4px; }
h2 { font-size:24px; color:var(--accent); margin:32px 0 10px; }
h3 { font-size:19px; margin:24px 0 8px; }
p.lede { color:var(--muted); max-width:80ch; margin:0 0 20px; }
a { color:var(--accent); }
table.idx { width:100%; border-collapse:collapse; background:var(--surface); border:1px solid var(--rule); }
table.idx th, table.idx td { text-align:left; vertical-align:top; padding:10px 12px; border-bottom:1px solid var(--rule); }
table.idx th { font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
table.idx img { width:120px; height:auto; display:block; border:1px solid var(--rule); background:#ddd; }
table.idx td.thumb { width:144px; }
table.idx .where { color:var(--muted); font-size:14px; }
table.idx .cat { color:var(--muted); font-size:14px; font-style:italic; }
.badge { display:inline-block; font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; border:1px solid var(--accent); color:var(--accent); padding:3px 8px; border-radius:3px; white-space:normal; }
.badge.medium { opacity:.8; } .badge.low { opacity:.6; } .badge.none { border-color:var(--muted); color:var(--muted); }
.crumbs { font-size:14px; color:var(--muted); margin-bottom:8px; }
.credit { font-size:13px; color:var(--muted); margin-top:28px; max-width:90ch; }
article table { border-collapse:collapse; margin:12px 0 18px; font-size:15px; background:var(--surface); border:1px solid var(--rule); }
article th, article td { text-align:left; vertical-align:top; padding:6px 10px; border-bottom:1px solid var(--rule); }
article th { font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
article code, article pre { font-family:var(--mono); font-size:14px; }
article pre { background:var(--surface); border:1px solid var(--rule); padding:12px; overflow-x:auto; white-space:pre-wrap; }
article ul { padding-left:22px; } article li { margin-bottom:6px; }
article blockquote { border-left:3px solid var(--rule); margin:12px 0; padding:2px 14px; color:var(--muted); }
@media (max-width:700px) { body { font-size:16px; } table.idx th:first-child, table.idx td.thumb { display:none; } table.idx td { padding:8px; } }
"""


def page(title, body, crumbs=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{STYLE}</style></head>
<body><div class="wrap"><p class="crumbs">Saved sets of all 22 fragments: <a href="runs/before-2026-09-22/index.html">Before</a> · <a href="runs/after-2026-09-22/index.html">After</a>.</p>{crumbs}{body}
<p class="credit">Images are served by the holding libraries through IIIF and are not stored in this repository; rights remain with the institutions named on each Fragmentarium record. Source and data: <a href="{REPO}">{REPO}</a>.</p>
</div></body></html>
"""


# --- a small Markdown subset: headings, paragraphs, lists, pipe tables, fenced code, blockquotes, inline code/bold/italic/links
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<i>\1</i>", s)
    s = re.sub(r"(?<![\"'>=\w/])(https?://[^\s<)]+)", r'<a href="\1">\1</a>', s)
    return s


def md_to_html(text):
    out, i, lines = [], 0, text.splitlines()
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre>" + html.escape("\n".join(lines[i + 1:j])) + "</pre>")
            i = j + 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lvl = min(len(m.group(1)) + 1, 4)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            if len(cells) >= 2 and all(re.match(r"^:?-{2,}:?$", c) for c in cells[1] if c):
                head, body = cells[0], cells[2:]
            else:
                head, body = None, cells
            t = ["<table>"]
            if head:
                t.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr>")
            for r in body:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</table>")
            out.append("".join(t))
            continue
        if re.match(r"^\s*[-*]\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                item = re.sub(r"^\s*[-*]\s+", "", lines[i])
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and not re.match(r"^\s*[-*]\s+", lines[i]):
                    item += " " + lines[i].strip()
                    i += 1
                items.append(f"<li>{inline(item)}</li>")
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if ln.startswith(">"):
            q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i].lstrip("> "))
                i += 1
            out.append("<blockquote>" + inline(" ".join(q)) + "</blockquote>")
            continue
        if not ln.strip():
            i += 1
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4}\s|\||```|>|\s*[-*]\s)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)


SORT_JS = """<script>
document.querySelectorAll('table.sortable th[data-col]').forEach(function(th){
  th.style.cursor='pointer'; th.title='Sort';
  th.addEventListener('click',function(){
    var t=th.closest('table'), c=+th.dataset.col, rows=Array.from(t.querySelectorAll('tr')).slice(1);
    var asc=!(th.dataset.asc==='1'); th.dataset.asc=asc?'1':'0';
    rows.sort(function(a,b){var x=a.cells[c].dataset.sort||a.cells[c].textContent.trim(), y=b.cells[c].dataset.sort||b.cells[c].textContent.trim(); return (x<y?-1:x>y?1:0)*(asc?1:-1);});
    rows.forEach(function(r){t.appendChild(r);});
  });
});
</script>"""


def badge(r):
    label = {"identified": "Identified", "partial": "Partial", "unidentified": "Not identified"}[r["status"]]
    conf = {"high": "high confidence", "medium": "medium confidence", "low": "low confidence", "none": ""}[r["confidence"]]
    return f'<span class="badge {r["confidence"]}">{label}{" · " + conf if conf else ""}</span>'


GENRE_BOOST = ("law", "decret", "canon", "gloss", "commentar", "sermon", "homil", "postil", "bible", "genesis",
               "psalm", "epist", "lexic", "etymolog", "vocabul", "grammar", "summa", "sentent", "breviar", "missal",
               "legend", "saint", "life of", "medic", "physic", "logic", "philosoph", "aristot")


def priority(row):
    """Rough 'was this text ever printed and is there enough of it to read' score, 0-100."""
    import math
    cents = [int(c) for c in re.findall(r"(\d+)th", row.get("century", ""))]
    c = max(cents) if cents else 0
    area = float(row.get("area_mm2") or 0)
    s = 0.0
    s += 35 * (1 if row.get("language") == "Latin" else 0.25)
    s += 30 * min(1.0, math.log10(max(area, 100)) / 5)          # 1 dm² leaf ≈ 0.8, a strip ≈ 0.55
    s += 25 * ({13: 0.8, 14: 1.0, 15: 1.0, 16: 0.9}.get(c, 0.5 if c else 0.4))
    title = (row.get("title", "") + " " + row.get("notes", "")).lower()
    s += 10 * (1 if any(k in title for k in GENRE_BOOST) else 0)
    return round(s)


def build_burndown(done):
    import csv
    src = sorted((ROOT / "data").glob("unidentified-*.csv"))[-1]
    rows = list(csv.DictReader(src.open()))
    for r in rows:
        r["priority"] = priority(r)
    rows.sort(key=lambda r: (-r["priority"], r["fragmentarium_id"]))
    n_done = sum(1 for r in rows if r["fragmentarium_id"] in done)
    trs = []
    for r in rows:
        fid = r["fragmentarium_id"]
        d = done.get(fid)
        if d:
            st = badge(d) + f' <a href="{fid}.html">page</a>'
        else:
            st = '<span class="badge none" style="opacity:.5">open</span>'
        trs.append("<tr>"
                   f'<td><a href="{r["url"]}">{fid}</a></td>'
                   f'<td>{html.escape(r["shelfmark"])}<br><span class="where">{html.escape(r["title"][:110])}</span></td>'
                   f'<td>{html.escape(r["century"])}</td><td>{html.escape(r["language"])}</td>'
                   f'<td>{html.escape(r["dimensions_mm"][:24])}</td><td>{r["priority"]}</td><td>{st}</td></tr>')
    body = ("<h1>Burndown</h1>"
            f'<p class="lede">All {len(rows)} Fragmentarium records whose title or summary says “unidentified” (sweep of '
            f'{src.name[13:23]}), ranked by a rough priority: Latin, large, 13th to 16th century, and a genre that was '
            f'likely printed score highest, because those are the ones a search can settle. {n_done} worked so far. '
            f'The list is a floor: records with vague titles that omit the word are not in it yet. '
            f'<a href="index.html">Back to results</a>.</p>'
            '<table class="idx"><tr><th>ID</th><th>Fragment · catalogue title</th><th>Century</th><th>Lang.</th><th>Size (mm)</th><th>Priority</th><th>Status</th></tr>'
            + "".join(trs) + "</table>")
    (DOCS / "burndown.html").write_text(page("Burndown · Fragmentarium", body))
    return len(rows), n_done


def build():
    data = json.loads((ROOT / "data" / "fragments.json").read_text())
    srank = {"identified": 0, "partial": 1, "unidentified": 2}
    crank = {"high": 0, "medium": 1, "low": 2, "none": 3}
    ordered = sorted(data, key=lambda r: (srank[r["status"]], crank[r["confidence"]], r["order"]))
    rows = []
    for r in ordered:
        rows.append(
            "<tr>"
            f'<td class="thumb"><a href="{r["id"]}.html"><img src="{html.escape(r["thumbnail"])}" alt="{r["id"]}" loading="lazy"></a></td>'
            f'<td><a href="{r["id"]}.html"><b>{html.escape(r["shelfmark"])}</b></a><br><span class="where">{html.escape(r["institution"])}</span>'
            f'<br><span class="cat">Catalogued as: {html.escape(r["catalogue_title"])}, {html.escape(r["catalogue_date"])}</span>'
            f'<br><span class="where"><a href="{r["record"]}">{r["id"]}</a></span></td>'
            f'<td>{html.escape(r["identification"])}<br><span class="where">{html.escape(r["note"])}</span></td>'
            f'<td data-sort="{srank[r["status"]]}{crank[r["confidence"]]}">{badge(r)}</td>'
            '</tr>'
        )
    n_id = sum(r["status"] == "identified" for r in data)
    n_p = sum(r["status"] == "partial" for r in data)
    n_u = sum(r["status"] == "unidentified" for r in data)
    body = (
        "<h1>Fragmentarium: identifying the unidentified</h1>"
        f'<p class="lede">Medieval manuscript fragments catalogued on <a href="https://fragmentarium.ms/">Fragmentarium</a> as '
        f'“unidentified”, worked one at a time: read from the library’s images, searched against printed editions and digital '
        f'corpora, with identifications supported by sustained agreement in distinctive wording and sequence. {len(data)} fragments so far: '
        f'{n_id} identified, {n_p} partial, {n_u} not identified. Each row links to a report with readings, comparisons, and remaining questions. '
        f'What remains: the <a href="burndown.html">burndown list</a> of every “unidentified” record, ranked. '
        f'Confidence refers to the identification or proposed source connection; transcription accuracy and verification coverage are separate. '
        f'Research and review were performed by LLMs. '
        f'Method in <a href="{REPO}/blob/main/METHOD.md">METHOD.md</a>; what the labels mean in <a href="{REPO}/blob/main/CONVENTIONS.md">CONVENTIONS.md</a>.</p>'
        '<table class="idx sortable"><tr><th></th><th data-col="1">Fragment</th><th>Our identification</th><th data-col="3">Confidence</th></tr>'
        + "".join(rows)
        + "</table>" + SORT_JS
    )
    (DOCS / "index.html").write_text(page("Fragmentarium: identifying the unidentified", body))
    for r in data:
        md = (ROOT / "fragments" / r["id"] / "README.md").read_text()
        crumbs = f'<div class="crumbs"><a href="index.html">All fragments</a> · <a href="{r["record"]}">Fragmentarium record</a> · <a href="{REPO}/tree/main/fragments/{r["id"]}">folder on GitHub</a></div>'
        head = (
            f"<h1>{html.escape(r['shelfmark'])} <span style='font-size:.6em;color:var(--muted)'>({r['id']})</span></h1>"
            f'<p class="lede">{html.escape(r["institution"])} · catalogued as {html.escape(r["catalogue_title"])}, {html.escape(r["catalogue_date"])}</p>'
            f"<p>{badge(r)}</p><p><b>{html.escape(r['identification'])}</b></p>"
            f'<p><img src="{html.escape(r["thumbnail"].replace("/240,/", "/600,/"))}" alt="{r["id"]}" style="max-width:100%;border:1px solid var(--rule)"></p>'
        )
        (DOCS / f"{r['id']}.html").write_text(page(f"{r['shelfmark']} · {r['id']}", head + "<article>" + md_to_html(md) + "</article>", crumbs))
    review = (ROOT / "REVIEW.md").read_text()
    (DOCS / "review.html").write_text(page(
        "Second-model review · Fragmentarium", "<article>" + md_to_html(review) + "</article>",
        '<div class="crumbs"><a href="index.html">All fragments</a></div>'))
    build_burndown({r["id"]: r for r in data})
    (DOCS / ".nojekyll").write_text("")
    return data


if __name__ == "__main__":
    d = build()
    print(f"built index + {len(d)} pages in {DOCS}")
