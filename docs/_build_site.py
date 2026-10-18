#!/usr/bin/env python3
"""Build the GitHub Pages site in docs/ from data/fragments.json and fragments/*/README.md.

Python 3, standard library only. From the repo root:

    python3 docs/_build_site.py

Writes docs/index.html (the table) and docs/<F-id>.html (one page per published identification, rendered from
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
details { margin-top:24px; } summary { cursor:pointer; color:var(--accent); }
button.sort { font:inherit; color:inherit; text-transform:inherit; letter-spacing:inherit; background:none; border:0; padding:0; cursor:pointer; text-align:left; }
article blockquote { border-left:3px solid var(--rule); margin:12px 0; padding:2px 14px; color:var(--muted); }
table.sortable th { white-space:nowrap; }
th[aria-sort=ascending] button.sort, th[aria-sort=descending] button.sort { color:var(--accent); }
table.burndown td:first-child { white-space:nowrap; }
th .filter { position:relative; display:inline-block; margin-left:6px; }
th .filter > button { font:inherit; font-size:11px; color:var(--muted); background:none; border:0; padding:0 2px; cursor:pointer; }
th.filtered, th.filtered .filter > button { color:var(--accent); }
.menu { position:absolute; right:0; top:22px; z-index:5; min-width:190px; background:var(--surface); border:1px solid var(--rule); border-radius:6px; padding:8px; box-shadow:0 4px 16px rgba(0,0,0,.12); text-transform:none; letter-spacing:0; font-size:15px; color:var(--ink); }
.menu[hidden] { display:none; }
.menu label { display:flex; gap:8px; align-items:center; padding:5px 6px; border-radius:4px; cursor:pointer; white-space:nowrap; }
.menu label:hover { background:var(--bg); }
.menu .count { margin-left:auto; color:var(--muted); font-size:13px; }
.menu button.all { font:inherit; font-size:13px; color:var(--accent); background:none; border:0; padding:4px 6px 2px; cursor:pointer; }
.shown { color:var(--muted); font-size:14px; margin:0 0 8px; }
@media (max-width:700px) { body { font-size:16px; } table.idx th.thumb, table.idx td.thumb { display:none; } table.idx td { padding:8px; } }
"""


def page(title, body, crumbs=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="icon" href="favicon.svg" type="image/svg+xml" sizes="any">
<style>{STYLE}</style></head>
<body><div class="wrap">{crumbs}{body}
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
  th.querySelector('button.sort').addEventListener('click',function(){
    var t=th.closest('table'), c=+th.dataset.col, body=t.tBodies[0], rows=Array.from(body.rows);
    var asc=th.getAttribute('aria-sort')!=='ascending', num=th.dataset.type==='num';
    t.querySelectorAll('th[data-col]').forEach(function(h){h.setAttribute('aria-sort','none');});
    th.setAttribute('aria-sort',asc?'ascending':'descending');
    function key(r){var cell=r.cells[c], v=cell.dataset.sort!==undefined?cell.dataset.sort:cell.textContent.trim(); return num?(v===''?null:parseFloat(v)):v.toLowerCase();}
    rows.sort(function(a,b){var x=key(a), y=key(b);
      if(x===null||x==='') return (y===null||y==='')?0:1; if(y===null||y==='') return -1;  // blanks last either way
      return (x<y?-1:x>y?1:0)*(asc?1:-1);});
    rows.forEach(function(r){body.appendChild(r);});
  });
});
</script>"""

FILTER_JS = """<script>
(function(){
  var th=document.querySelector('th[data-filter]'); if(!th) return;
  var t=th.closest('table'), c=+th.dataset.col, btn=th.querySelector('.filter > button'), menu=th.querySelector('.menu');
  var boxes=Array.from(menu.querySelectorAll('input')), shown=document.getElementById('shown');
  function apply(){
    var on=boxes.filter(function(b){return b.checked;}).map(function(b){return b.value;}), n=0, rows=t.tBodies[0].rows;
    for(var i=0;i<rows.length;i++){var ok=on.indexOf(rows[i].cells[c].dataset.status)>=0; rows[i].hidden=!ok; if(ok) n++;}
    th.classList.toggle('filtered', on.length<boxes.length);
    shown.textContent='Showing '+n+' of '+rows.length+(on.length<boxes.length?' ('+on.join(', ')+')':'');
  }
  boxes.forEach(function(b){b.addEventListener('change',apply);});
  menu.querySelector('button.all').addEventListener('click',function(){boxes.forEach(function(b){b.checked=true;}); apply();});
  btn.addEventListener('click',function(e){e.stopPropagation(); menu.hidden=!menu.hidden; btn.setAttribute('aria-expanded',!menu.hidden);});
  menu.addEventListener('click',function(e){e.stopPropagation();});
  document.addEventListener('click',function(){menu.hidden=true; btn.setAttribute('aria-expanded','false');});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){menu.hidden=true; btn.setAttribute('aria-expanded','false');}});
  apply();
})();
</script>"""


def publishable(row):
    # `known_from` marks an identification the scholarship had already published for this fragment:
    # recorded in the ledger, kept off the site and out of its count.
    return row["status"] == "identified" and row["confidence"] == "high" and not row.get("known_from")


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
    sweeps = sorted((ROOT / "data").glob("unidentified-*.csv"))
    src = sweeps[-1]
    rows = [r for r in csv.DictReader(src.open()) if r.get("scope", "title") == "title"]
    # A worked record that a later sweep no longer finds (the catalogue has since retitled it) stays listed.
    listed = {r["fragmentarium_id"] for r in rows}
    for older in reversed(sweeps[:-1]):
        for r in csv.DictReader(older.open()):
            if r["fragmentarium_id"] in done and r["fragmentarium_id"] not in listed:
                rows.append(r)
                listed.add(r["fragmentarium_id"])
    for r in rows:
        r["priority"] = priority(r)
    rows.sort(key=lambda r: (-r["priority"], r["fragmentarium_id"]))
    n_done = sum(1 for r in rows if r["fragmentarium_id"] in done)
    statuses = {"identified": "Identified", "examined": "Examined", "open": "Open"}
    counts = {key: 0 for key in statuses}
    trs = []
    for r in rows:
        fid = r["fragmentarium_id"]
        d = done.get(fid)
        if d and publishable(d):
            st, key = f'<a href="{fid}.html">Identified</a>', "identified"
        elif d and d.get("known_from"):
            st, key = 'Examined; already identified in the literature', "examined"
        elif d:
            st, key = 'Examined; not identified', "examined"
        else:
            st, key = '<span class="badge none" style="opacity:.5">open</span>', "open"
        counts[key] += 1
        century = re.search(r"(\d+)(?:st|nd|rd|th)", r.get("century", ""))
        trs.append("<tr>"
                   f'<td><a href="{r["url"]}">{fid}</a></td>'
                   f'<td>{html.escape(r["shelfmark"])}<br><span class="where">{html.escape(r["title"][:110])}</span></td>'
                   f'<td data-sort="{century.group(1) if century else ""}">{html.escape(r["century"])}</td><td>{html.escape(r["language"])}</td>'
                   f'<td data-sort="{r.get("area_mm2") or ""}">{html.escape(r["dimensions_mm"][:24])}</td><td>{r["priority"]}</td>'
                   f'<td data-status="{key}" data-sort="{list(statuses).index(key)}">{st}</td></tr>')
    sortable = lambda col, label, kind="": (f'<th data-col="{col}" aria-sort="none"{f" data-type=\"{kind}\"" if kind else ""}>'
                                            f'<button class="sort" type="button">{label} ↕</button>')
    menu = "".join(f'<label><input type="checkbox" value="{key}" checked> {name}<span class="count">{counts[key]}</span></label>'
                   for key, name in statuses.items())
    head = ("<thead><tr>" + sortable(0, "ID") + "</th>" + sortable(1, "Fragment · catalogue title") + "</th>"
            + sortable(2, "Century", "num") + "</th>" + sortable(3, "Lang.") + "</th>"
            + sortable(4, "Size (mm)", "num") + "</th>"
            + '<th data-col="5" aria-sort="descending" data-type="num"><button class="sort" type="button">Priority ↕</button></th>'
            + sortable(6, "Status", "num").replace("<th ", "<th data-filter ")
            + '<span class="filter"><button type="button" aria-haspopup="true" aria-expanded="false" aria-label="Filter by status">▾</button>'
            f'<div class="menu" hidden>{menu}<button class="all" type="button">Show all</button></div></span></th></tr></thead>')
    body = ("<h1>Burndown</h1>"
            f'<p class="lede">All {len(rows)} Fragmentarium records whose title or summary says “unidentified”, “unknown” or the same in another language (sweep of '
            f'{src.name[13:23]}), ranked by a rough priority: Latin, large, 13th to 16th century, and a genre that was '
            f'likely printed score highest, because those are the ones a search can settle. {n_done} worked so far. '
            f'Size sorts by area. The list is a floor: records with vague titles that omit the word are not in it yet. '
            f'<a href="index.html">Back to results</a>.</p>'
            '<p class="shown" id="shown"></p>'
            '<table class="idx sortable burndown">' + head + "<tbody>"
            + "".join(trs) + "</tbody></table>" + SORT_JS + FILTER_JS)
    (DOCS / "burndown.html").write_text(page("Burndown · Fragmentarium", body))
    return len(rows), n_done


def build():
    data = json.loads((ROOT / "data" / "fragments.json").read_text())
    published = [r for r in data if publishable(r)]
    ordered = sorted(published, key=lambda r: (r["identified_on"], -r["order"]), reverse=True)
    published_ids = {r["id"] for r in published}
    # Remove obsolete current reports, including results later withdrawn. Historical runs stay intact.
    for path in DOCS.glob("F-*.html"):
        if path.stem not in published_ids:
            path.unlink()
    (DOCS / "review.html").unlink(missing_ok=True)
    rows = []
    for r in ordered:
        rows.append(
            "<tr>"
            f'<td class="thumb"><a href="{r["id"]}.html"><img src="{html.escape(r["thumbnail"])}" alt="{r["id"]}" loading="lazy"></a></td>'
            f'<td><a href="{r["id"]}.html"><b>{html.escape(r["shelfmark"])}</b></a><br><span class="where">{html.escape(r["institution"])}</span>'
            f'<br><span class="cat">Catalogued as: {html.escape(r["catalogue_title"])}, {html.escape(r["catalogue_date"])}</span>'
            f'<br><span class="where"><a href="{r["record"]}">{r["id"]}</a></span></td>'
            f'<td>{html.escape(r["identification"])}<br><span class="where">{html.escape(r["note"])}</span></td>'
            f'<td data-sort="{r["identified_on"]}"><time datetime="{r["identified_on"]}">{r["identified_on"]}</time></td>'
            '</tr>'
        )
    body = (
        "<h1>Fragmentarium: identifying the unidentified</h1>"
        f'<p class="lede">{len(published)} identifications of medieval manuscript fragments catalogued on '
        f'<a href="https://fragmentarium.ms/">Fragmentarium</a> as “unidentified”. '
        f'Each report links the manuscript to the matching edition and explains the evidence. '
        f'Research and comparisons were performed by LLMs. '
        f'<a href="{REPO}/blob/main/METHOD.md">Method</a>.</p>'
        '<table class="idx sortable"><thead><tr><th class="thumb"></th><th data-col="1" aria-sort="none"><button class="sort" type="button">Fragment ↕</button></th>'
        '<th>Identification</th><th data-col="3" aria-sort="descending"><button class="sort" type="button">Date identified ↕</button></th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table>" + SORT_JS
        + f'<p class="credit">{len(data)} fragments examined. Dates record the original identification, not later reviews. '
        f'<a href="burndown.html">Research progress</a> · <a href="{REPO}/blob/main/data/fragments.json">Research ledger</a>.</p>'
    )
    (DOCS / "index.html").write_text(page("Fragmentarium: identifying the unidentified", body))
    for r in ordered:
        md = (ROOT / "fragments" / r["id"] / "README.md").read_text()
        crumbs = f'<div class="crumbs"><a href="index.html">All identifications</a> · <a href="{r["record"]}">Fragmentarium record</a> · <a href="{REPO}/tree/main/fragments/{r["id"]}">folder on GitHub</a></div>'
        head = (
            f"<h1>{html.escape(r['shelfmark'])} <span style='font-size:.6em;color:var(--muted)'>({r['id']})</span></h1>"
            f'<p class="lede">{html.escape(r["institution"])} · catalogued as {html.escape(r["catalogue_title"])}, {html.escape(r["catalogue_date"])}</p>'
            f"<p><b>{html.escape(r['identification'])}</b></p>"
            f'<p>{html.escape(r["note"])}</p>'
            f'<p><a href="{html.escape(r["verify"])}">Matching edition passage</a> · '
            f'<a href="{html.escape(r["record"])}">Manuscript images</a></p>'
            f'<p class="where">Identified <time datetime="{r["identified_on"]}">{r["identified_on"]}</time>.</p>'
            f'<p><img src="{html.escape(r["thumbnail"].replace("/240,/", "/600,/"))}" alt="{r["id"]}" style="max-width:100%;border:1px solid var(--rule)"></p>'
        )
        (DOCS / f"{r['id']}.html").write_text(page(f"{r['shelfmark']} · {r['id']}", head + "<details><summary>Readings and comparison details</summary><article>" + md_to_html(md) + "</article></details>", crumbs))
    build_burndown({r["id"]: r for r in data})
    (DOCS / ".nojekyll").write_text("")
    return published


if __name__ == "__main__":
    d = build()
    print(f"built index + {len(d)} pages in {DOCS}")
