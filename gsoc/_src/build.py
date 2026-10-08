#!/usr/bin/env python3
"""Builds the pages in gsoc/ from the markdown in _src/pages.

    python3 gsoc/_src/build.py

The markdown carries the writing. This script adds the shell every page shares
(explorer, graph, table of contents), draws the diagrams, and fills the pull
request tables and records from _src/data. Statuses in the built pages are the
ones known at build time, and pr-status.js refreshes them in the browser.
"""

import datetime
import html
import json
import os
import re
import sys

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import diagrams  # noqa: E402
from build_media import fig as figure, vid as video  # noqa: E402
import records  # noqa: E402

REPO = 'https://github.com/omegaup/omegaup'
SITE = 'https://prasannamishra001.github.io/prasannamishra/gsoc/'
TODAY = datetime.date.today()
MONTHS = diagrams.MONTHS


def load(name):
    with open(os.path.join(HERE, 'data', name), encoding='utf-8') as f:
        return json.load(f)


PRS = load('prs.json')
ISSUES = load('issues.json')
COMMENTS = load('comments.json')
PR_BY = {p['number']: p for p in PRS}
ISSUE_BY = {i['number']: i for i in ISSUES}

PAGES = [
    # slug, explorer label, folder, kind, card text
    ('index', 'Summary', 'gsoc-2026', 'hub',
     'The summer on one page.'),
    ('control-plane', 'Cron control plane', 'gsoc-2026', 'project',
     'Run history, a lock, an admin page and a safe rerun for every background job.'),
    ('model-training', 'Model training', 'gsoc-2026', 'project',
     'The recommendation model, trained on a schedule and refused when it gets worse.'),
    ('health-checks', 'Problem health checks', 'gsoc-2026', 'project',
     'A nightly job that finds problems which quietly stopped working.'),
    ('groundwork', 'Tests and query fixes', 'gsoc-2026', 'page',
     'The first half: the proposal, the tests, and the promise I took back.'),
    ('alongside', 'Alongside the project', 'gsoc-2026', 'page',
     'Navigation menus, a view unavailable page, and system settings.'),
    ('lessons', 'What I learned', 'gsoc-2026', 'page',
     'The bugs I wrote, the things I got wrong, and what I do differently now.'),
    ('before-gsoc', 'Before the summer', 'journey', 'page',
     'August 2025 to May 2026: the first fifty seven pull requests.'),
    ('after-gsoc', 'After the summer', 'journey', 'page',
     'What has landed since 24 August, and what is still moving.'),
    ('journey', 'Timeline', 'journey', 'page',
     'Every month since the first pull request, in order.'),
    ('pull-requests', 'Pull requests', 'records', 'page',
     'Every pull request I have opened on omegaUp, with its status.'),
    ('issues', 'Issues', 'records', 'page',
     'Every issue I have filed.'),
    ('reviews', 'Reviews', 'records', 'page',
     'What reviewers asked for, and the threads where I helped someone else.'),
]
PAGE_BY = {p[0]: p for p in PAGES}
FOLDERS = ['gsoc-2026', 'journey', 'records']


def esc(text):
    return html.escape(str(text), quote=True)


def nice_date(iso, year=True):
    d = datetime.date.fromisoformat(iso)
    return f'{d.day} {MONTHS[d.month - 1]}' + (f' {d.year}' if year else '')


def pr_state(pr):
    if pr['merged']:
        return 'merged'
    if pr['closed']:
        return 'closed'
    return 'draft' if pr['draft'] else 'in review'


def state_cell(kind, number, state, tag='td'):
    cls = 'pr-state pr-state-' + state.replace(' ', '-')
    return f'<{tag} class="{cls}" data-state-for="{kind}/{number}">{state}</{tag}>'


# ----------------------------------------------------------------- pieces

def diagram_block(svg, caption, extra=''):
    cap = f'<figcaption>{caption}</figcaption>' if caption else ''
    return f'<figure class="diagram reveal"><div class="diagram-body">{svg}</div>{extra}{cap}</figure>'


def table(head, rows, cls=''):
    out = [f'<div class="table-container"><table{cls}><thead><tr>']
    out += [f'<th>{h}</th>' for h in head]
    out.append('</tr></thead><tbody>')
    for row in rows:
        out.append('<tr>' + ''.join(c if c.startswith('<td') else f'<td>{c}</td>' for c in row) + '</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)


def pr_link(n):
    return f'<a href="{REPO}/pull/{n}">#{n}</a>'


def issue_link(n):
    return f'<a href="{REPO}/issues/{n}">#{n}</a>'


def pr_rows(numbers):
    rows = []
    for n in numbers:
        pr = PR_BY[n]
        rec = records.R.get(n, {})
        name = rec.get('title') or pr['title']
        rows.append([pr_link(n), esc(name), f'<td class="num">{nice_date(pr["created"])}</td>',
                     state_cell('pull', n, pr_state(pr))])
    return rows


def pr_table(numbers):
    return table(['PR', 'What it does', 'Opened', 'Status'], pr_rows(numbers))


def all_pr_table():
    out = ['<div class="filter" data-for="all-prs"><input type="search" placeholder="filter by number or words" '
           'aria-label="Filter pull requests" />'
           '<button type="button" data-state="merged" aria-pressed="false">merged</button>'
           '<button type="button" data-state="in review|approved|draft" aria-pressed="false">open</button>'
           '<button type="button" data-state="closed" aria-pressed="false">closed</button>'
           '<span class="count"></span></div>',
           '<div class="table-container"><table id="all-prs" data-live-rows="pull"><thead><tr>'
           '<th>PR</th><th>What it does</th><th>Opened</th><th>Status</th></tr></thead><tbody>']
    seen = set()
    for title, numbers in records.ERAS:
        out.append(f'<tr class="group-row"><td colspan="4">{title}</td></tr>')
        for row in pr_rows(numbers):
            out.append('<tr>' + ''.join(c if c.startswith('<td') else f'<td>{c}</td>' for c in row) + '</tr>')
        seen.update(numbers)
    missing = [p['number'] for p in PRS if p['number'] not in seen]
    if missing:
        raise SystemExit(f'pull requests missing from records.ERAS: {missing}')
    out.append('</tbody></table></div>')
    return ''.join(out)


KIND_ORDER = ['feature', 'bug', 'security', 'infra', 'cleanup']
KIND_NAME = {'feature': 'Features I proposed', 'bug': 'Bugs I reported', 'security': 'Security reports',
             'infra': 'Development environment, CI and tooling', 'cleanup': 'Cleanups and refactors'}


def issue_table():
    out = ['<div class="filter" data-for="all-issues"><input type="search" placeholder="filter by number or words" '
           'aria-label="Filter issues" />'
           '<button type="button" data-state="completed" aria-pressed="false">completed</button>'
           '<button type="button" data-state="open" aria-pressed="false">open</button>'
           '<span class="count"></span></div>',
           '<div class="table-container"><table id="all-issues" data-live-rows="issues"><thead><tr>'
           '<th>Issue</th><th>What it asks for</th><th>Opened</th><th>Status</th><th>Closed by</th>'
           '</tr></thead><tbody>']
    for kind in KIND_ORDER:
        group = sorted((i for i in ISSUES if i['kind'] == kind), key=lambda i: i['number'])
        out.append(f'<tr class="group-row"><td colspan="5">{KIND_NAME[kind]} ({len(group)})</td></tr>')
        for i in group:
            title = re.sub(r'^\s*\[[^\]]+\]\s*:?\s*', '', i['title'])
            fixed = ', '.join(pr_link(n) for n in i['fixed_by']) or ''
            out.append(f'<tr><td>{issue_link(i["number"])}</td><td>{esc(title)}</td>'
                       f'<td class="num">{nice_date(i["created"])}</td>'
                       f'{state_cell("issues", i["number"], i["state"])}<td>{fixed}</td></tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)


def comments_table():
    rows = []
    for c in sorted(COMMENTS, key=lambda c: c['date']):
        kind = 'pull' if c['type'] == 'pr' else 'issues'
        link = f'<a href="{REPO}/{kind}/{c["number"]}">#{c["number"]}</a>'
        rows.append([link, f'<td class="num">{nice_date(c["date"])}</td>', esc(records.COMMENT_NOTES.get(c['number'], c['what']))])
    return table(['Thread', 'When', 'What I added'], rows)


def record(n):
    pr = PR_BY[n]
    rec = records.R[n]
    state = pr_state(pr)
    meta = [f'<span>opened {nice_date(pr["created"])}</span>']
    opened = datetime.date.fromisoformat(pr['created'])
    if pr['merged']:
        days = (datetime.date.fromisoformat(pr['merged']) - opened).days
        meta.append(f'<span>merged {nice_date(pr["merged"])}, after {days} day{"s" if days != 1 else ""}</span>')
    elif pr['closed']:
        meta.append(f'<span>closed {nice_date(pr["closed"])}</span>')
    if pr['additions'] is not None and not rec.get('hide_size'):
        meta.append(f'<span class="add">+{pr["additions"]}</span><span class="del">&minus;{pr["deletions"]}</span>'
                    f'<span>{pr["files"]} file{"s" if pr["files"] != 1 else ""}</span>')
    if pr['issues']:
        meta.append('<span>issue ' + ', '.join(issue_link(i) for i in pr['issues'][:2]) + '</span>')
    out = [f'<section class="record" id="pr-{n}"><div class="record-head">'
           f'<a class="n" href="{REPO}/pull/{n}">#{n}</a><h4>{esc(rec.get("title") or pr["title"])}</h4>'
           f'{state_cell("pull", n, state, "span")}</div>'
           f'<div class="record-meta">{"".join(meta)}</div>']
    for para in rec['text'].strip().split('\n\n'):
        out.append(f'<p>{para.strip()}</p>')
    if rec.get('review'):
        out.append('<div class="review">')
        for who, text in rec['review']:
            out.append(f'<p><span class="who">{who}</span> {text}</p>')
        out.append('</div>')
    out.append(rec.get('media', ''))
    out.append('</section>')
    return ''.join(out)


def stats_block(kind):
    period = [p for p in PRS if '2026-05-26' <= p['created'] <= '2026-08-24']
    merged_in = [p for p in PRS if p['merged'] and '2026-05-26' <= p['merged'] <= '2026-08-24']
    if kind == 'gsoc':
        cells = [(len(period), 'opened', 'pull requests opened in the coding period'),
                 (sum(1 for p in period if p['merged']), 'merged', 'of those merged so far'),
                 (len(merged_in), 'merged-in-period', 'merged between 26 May and 24 August'),
                 (5, None, 'cron jobs recording every run'),
                 (4, None, 'new tables on main')]
    else:
        cells = [(len(PRS), 'all-opened', 'pull requests since August 2025'),
                 (sum(1 for p in PRS if p['merged']), 'all-merged', 'merged'),
                 (sum(1 for p in PRS if not p['merged'] and not p['closed']), 'all-open', 'open'),
                 (len(ISSUES), 'issues-all', 'issues filed'),
                 (len(COMMENTS), None, 'threads where I helped on someone else\'s work')]
    out = ['<div class="stats reveal">']
    for value, live, label in cells:
        attr = f' data-count="{live}"' if live else ''
        out.append(f'<div class="stat"><b{attr}>{value}</b><span>{label}</span></div>')
    out.append('</div>')
    return ''.join(out)


def cards(slugs):
    out = ['<div class="cards">']
    for slug in slugs:
        _, label, folder, _, text = PAGE_BY[slug]
        out.append(f'<a class="card reveal" href="{slug}.html"><span class="k">{folder}</span>'
                   f'<h4>{label}</h4><p>{text}</p><span class="go">read &rarr;</span></a>')
    out.append('</div>')
    return ''.join(out)


def chart(name, caption):
    if name == 'monthly':
        svg, rows = diagrams.monthly(PRS, TODAY)
        legend = ('<div class="legend"><span class="a"><i></i>opened</span><span class="b"><i></i>merged</span>'
                  '<span class="band"><i></i>GSoC coding period</span></div>')
        body = table(['Month', 'Opened', 'Merged'], [[a, str(b), str(c)] for a, b, c in rows])
    else:
        names = {n: r['name'] for n, r in records.R.items() if r.get('name')}
        svg, rows = diagrams.waiting(PRS, names, TODAY)
        legend = ('<div class="legend"><span class="b"><i></i>opened to merged</span>'
                  '<span class="o"><i></i>still open</span><span class="w"><i></i>closed without merging</span>'
                  '<span class="band"><i></i>GSoC coding period</span></div>')
        body = table(['PR', 'What', 'Opened', 'Outcome', 'Days'],
                     [[pr_link(n), esc(name), nice_date(c), word, str(days)] for n, name, c, word, days in rows])
    extra = f'<details class="as-table"><summary>show this as a table</summary>{body}</details>'
    cap = f'<figcaption>{caption}</figcaption>' if caption else ''
    return (f'<figure class="diagram reveal">{legend}<div class="diagram-body">{svg}</div>{extra}{cap}</figure>')


DIAGRAMS = {
    'architecture': diagrams.architecture,
    'runner': diagrams.runner,
    'rerun': diagrams.rerun,
    'guardrail': diagrams.guardrail,
    'finding': diagrams.finding,
    'stack': lambda: diagrams.stack(PR_BY),
}


def shortcode(match):
    name, _, rest = match.group(1).strip().partition(' ')
    args = [a.strip() for a in rest.split('|')] if rest.strip() else []
    if name == 'fig':
        return figure(*args)
    if name == 'video':
        return video(*args)
    if name == 'pair':
        a, tag_a, b, tag_b = args[:4]
        caption = args[4] if len(args) > 4 else ''
        cap = f'<figcaption>{caption}</figcaption>' if caption else ''
        return ('<div class="fig-row reveal">'
                f'<div><span class="tag">{tag_a}</span>{figure(a, "", "l")}</div>'
                f'<div><span class="tag">{tag_b}</span>{figure(b, "", "l")}</div>{cap}</div>').replace(
                    'zoomable reveal', 'zoomable')
    if name == 'gallery':
        caption = ''
        if '||' in rest:
            rest, caption = rest.split('||', 1)
        items = []
        for item in rest.split(';;'):
            src, _, cap = item.partition('::')
            items.append(figure(src.strip(), cap.strip(), 'l').replace('zoomable reveal', 'zoomable'))
        cap = f'<figcaption>{caption.strip()}</figcaption>' if caption.strip() else ''
        return f'<div class="gallery reveal">{"".join(items)}{cap}</div>'
    if name == 'diagram':
        return diagram_block(DIAGRAMS[args[0]](), args[1] if len(args) > 1 else '')
    if name == 'chart':
        return chart(args[0], args[1] if len(args) > 1 else '')
    if name == 'stats':
        return stats_block(args[0])
    if name == 'cards':
        return cards([a.strip() for a in rest.split(',')])
    if name == 'prtable':
        if args[0] == 'all':
            return all_pr_table()
        return pr_table(records.GROUPS[args[0]])
    if name == 'records':
        return ''.join(autolink(record(n)) for n in records.GROUPS[args[0]])
    if name == 'issuetable':
        return issue_table()
    if name == 'comments':
        return comments_table()
    if name == 'issuerows':
        rows = [[issue_link(n), esc(re.sub(r'^\s*\[[^\]]+\]\s*:?\s*', '', ISSUE_BY[n]['title'])),
                 state_cell('issues', n, ISSUE_BY[n]['state'])] for n in records.ISSUE_GROUPS[args[0]]]
        return table(['Issue', 'What it asks for', 'Status'], rows)
    raise SystemExit(f'unknown shortcode: {name}')


FORMATTER = HtmlFormatter(nowrap=True)


def code_block(match):
    lang, name, body = match.group(1), (match.group(2) or '').strip(), match.group(3)
    try:
        marked = highlight(body, get_lexer_by_name(lang), FORMATTER)
    except Exception:
        marked = esc(body)
    label = f'<span class="file">{esc(name)}</span>' if name else '<span class="file"></span>'
    return (f'<div class="codeblock reveal"><div class="codeblock-head">{label}<span class="lang">{lang}</span>'
            f'<button type="button">copy</button></div><pre class="hl"><code>{marked.rstrip()}</code></pre></div>')


def autolink(markup):
    """Turns a bare #9998 into a link, leaving links, code and drawings alone."""
    out, depth = [], 0
    skip = re.compile(r'<(/?)(a|code|pre|svg|h1|h2|h3|h4|button|summary)\b', re.I)
    for part in re.split(r'(<[^>]+>)', markup):
        if part.startswith('<'):
            m = skip.match(part)
            if m and not part.endswith('/>'):
                depth += -1 if m.group(1) else 1
            out.append(part)
        elif depth == 0:
            def link(m):
                n = int(m.group(1))
                kind = 'pull' if n in PR_BY else 'issues'
                return f'<a href="{REPO}/{kind}/{n}">#{n}</a>'
            out.append(re.sub(r'(?<![\w&/])#(\d{4,5})\b', link, part))
        else:
            out.append(part)
    return ''.join(out)


def render_markdown(text):
    blocks = []

    def stash(markup):
        blocks.append(markup)
        return f'\n\n<div data-block="{len(blocks) - 1}"></div>\n\n'

    text = re.sub(r'^```(\w+)[ \t]*([^\n]*)\n(.*?)^```[ \t]*$', lambda m: stash(code_block(m)), text, flags=re.S | re.M)
    text = re.sub(r'^\{\{(.+?)\}\}[ \t]*$', lambda m: stash(shortcode(m)), text, flags=re.S | re.M)
    body = markdown.markdown(text, extensions=['extra', 'sane_lists'])
    body = body.replace('<table>', '<div class="table-container"><table>').replace('</table>', '</table></div>')
    body = autolink(body)
    body = re.sub(r'<div data-block="(\d+)"></div>', lambda m: blocks[int(m.group(1))], body)
    return body


def headings(body):
    toc = []

    def mark(m):
        level, ident, inner = m.group(1), m.group(2), m.group(3)
        plain = re.sub(r'<[^>]+>', '', inner)
        toc.append((int(level), ident, plain))
        return (f'<h{level} id="{ident}">{inner}<a role="anchor" aria-hidden="true" tabindex="-1" '
                f'href="#{ident}" class="anchor">#</a></h{level}>')
    body = re.sub(r'<h([23]) id="([^"]+)">(.*?)</h\1>', mark, body, flags=re.S)
    return body, toc


FOLD = ('<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="fold">'
        '<polyline points="6 9 12 15 18 9"></polyline></svg>')
CHEVRON = ('<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" '
           'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
           'class="folder-icon"><polyline points="9 18 15 12 9 6"></polyline></svg>')
SUN = ('<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
       'stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22'
       'M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/></svg>')
MOON = ('<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>')
EXPAND = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
          'stroke-linejoin="round"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>')


def explorer(current):
    out = []
    for folder in FOLDERS:
        out.append(f'<li><button type="button" class="folder-container" data-fold="folder-{folder}">{CHEVRON}'
                   f'<span class="folder-title">{folder}</span></button><ul id="folder-{folder}">')
        for slug, label, f, _, _ in PAGES:
            if f == folder:
                cls = ' class="active"' if slug == current else ''
                out.append(f'<li><a href="{slug}.html"{cls}>{label}</a></li>')
        out.append('</ul></li>')
    out.append(f'<li><button type="button" class="folder-container" data-fold="folder-elsewhere">{CHEVRON}'
               '<span class="folder-title">elsewhere</span></button><ul id="folder-elsewhere">'
               '<li><a href="../index.html">Back to the portfolio</a></li>'
               f'<li><a href="{REPO}/pulls?q=is%3Apr+author%3APrasannaMishra001">My pull requests on GitHub</a></li>'
               f'<li><a href="{REPO}/issues/9992">The control plane issue</a></li>'
               '<li><a href="https://summerofcode.withgoogle.com/">Google Summer of Code</a></li></ul></li>')
    return ''.join(out)


def front_matter(text):
    meta = {}
    if text.startswith('---'):
        _, head, text = text.split('---', 2)
        for line in head.strip().splitlines():
            key, _, value = line.partition(':')
            meta[key.strip()] = value.strip()
    return meta, text


def page(slug, meta, body, toc):
    label = PAGE_BY[slug][1]
    title = meta['title']
    words = len(re.sub(r'<[^>]+>', ' ', body).split())
    minutes = max(1, round(words / 230))
    crumbs = ['<div class="breadcrumb-element"><a href="../index.html">Home</a><p>&#10095;</p></div>']
    if slug == 'index':
        crumbs.append('<div class="breadcrumb-element"><a href="index.html">gsoc 2026 omegaup</a></div>')
    else:
        crumbs.append('<div class="breadcrumb-element"><a href="index.html">gsoc 2026 omegaup</a><p>&#10095;</p></div>')
        crumbs.append(f'<div class="breadcrumb-element"><a href="{slug}.html">{label.lower()}</a></div>')
    toc_html = ''.join(f'<li class="depth-{level - 2}"><a href="#{ident}">{esc(text)}</a></li>'
                       for level, ident, text in toc)
    order = [p[0] for p in PAGES]
    i = order.index(slug)
    prev_next = '<div class="next-prev">'
    for j, word in ((i - 1, 'previous'), (i + 1, 'next')):
        if 0 <= j < len(order):
            s, lab, _, _, text = PAGE_BY[order[j]]
            arrow = '&larr; ' if word == 'previous' else ''
            arrow2 = ' &rarr;' if word == 'next' else ''
            prev_next += (f'<a class="card" href="{s}.html"><span class="k">{word}</span>'
                          f'<h4>{arrow}{lab}{arrow2}</h4><p>{text}</p></a>')
        else:
            prev_next += '<span></span>'
    prev_next += '</div>'
    updated = nice_date(TODAY.isoformat())
    wide = ' class="wide"' if meta.get('wide') else ''
    canonical = SITE if slug == 'index' else f'{SITE}{slug}.html'
    scripts = '<script src="graph-data.js"></script><script src="quartz.js"></script>'
    if 'data-state-for' in body or 'data-count' in body:
        scripts += '<script src="pr-status.js"></script>'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(title)} | Prasanna Mishra</title>
<meta name="description" content="{esc(meta.get('description', ''))}" />
<meta name="author" content="Prasanna Mishra" />
<meta name="theme-color" content="#faf8f8" />
<link rel="canonical" href="{canonical}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(meta.get('description', ''))}" />
<meta property="og:type" content="article" />
<link rel="icon" type="image/svg+xml" href="assets/gsoc-icon.svg" />
<script>(function(){{try{{var t=localStorage.getItem('gsoc-theme');if(t!=='dark'&&t!=='light')t=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.setAttribute('data-theme',t);}}catch(e){{document.documentElement.setAttribute('data-theme','light');}}}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=Besley:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="quartz.css" />
</head>
<body data-page="{slug}">
<div class="progress" aria-hidden="true"><i></i></div>
<div id="quartz-root" class="page"><div id="quartz-body">

<div class="left sidebar">
  <div>
    <div class="site-head">
      <h2 class="page-title"><a href="index.html">Prasanna Mishra</a></h2>
      <button type="button" class="theme-toggle" id="theme-toggle" aria-label="Switch between light and dark" title="Switch between light and dark">{SUN}{MOON}</button>
    </div>
    <p class="site-tag">google summer of code 2026 &middot; omegaup</p>
  </div>
  <div class="sidebar-logos">
    <img src="assets/gsoc-logo.svg" alt="Google Summer of Code" class="gsoc-mark" />
    <img src="assets/omegaup-logo.png" alt="omegaUp" class="org-mark" />
  </div>
  <div class="explorer"><button type="button" class="explorer-toggle" data-fold="explorer-content"><h2>Explorer</h2>{FOLD}</button><div class="explorer-content" id="explorer-content"><ul class="explorer-ul">{explorer(slug)}</ul></div></div>
  <p class="sidebar-updated"><span class="pulse"></span>still going &middot; updated {updated}</p>
</div>

<div class="center">
  <div class="page-header">
    <nav class="breadcrumb-container" aria-label="breadcrumbs">{''.join(crumbs)}</nav>
    <h1 class="article-title">{title}</h1>
    <p class="content-meta"><time datetime="{TODAY.isoformat()}">updated {updated}</time><span>{minutes} min read</span></p>
  </div>
  <article{wide}>
{body}
{prev_next}
  </article>
  <footer class="site-footer">
    <p>Written by Prasanna Mishra &middot; <a href="mailto:mishra.prasanna838@gmail.com">email</a> &middot; <a href="https://github.com/PrasannaMishra001">github</a> &middot; <a href="https://www.linkedin.com/in/prasanna-mishra-871269367">linkedin</a></p>
    <p>This page was last built on {updated}. The work is not finished, so it will change.</p>
  </footer>
</div>

<div class="right sidebar">
  <div class="graph desktop-only">
    <div class="graph-head"><h3>Graph View</h3><button type="button" class="icon-btn" id="graph-open" aria-label="Open the full graph" title="Open the full graph">{EXPAND}</button></div>
    <div class="graph-container" id="graph-container"></div>
  </div>
  <div class="toc desktop-only"><button type="button" class="toc-toggle" data-fold="toc-content"><h3>Table of Contents</h3>{FOLD}</button><ul class="toc-content" id="toc-content">{toc_html}</ul></div>
</div>

</div></div>
{scripts}
</body>
</html>
'''


def main():
    built = {}
    for slug, *_ in PAGES:
        with open(os.path.join(HERE, 'pages', slug + '.md'), encoding='utf-8') as f:
            meta, text = front_matter(f.read())
        body, toc = headings(render_markdown(text))
        built[slug] = (meta, body, toc)

    links = set()
    for slug, (_, body, _) in built.items():
        for target in re.findall(r'href="([a-z-]+)\.html', body):
            if target in PAGE_BY and target != slug:
                links.add(tuple(sorted((slug, target))))
    nodes = [{'id': s, 'label': label, 'href': s + '.html', 'kind': kind} for s, label, _, kind, _ in PAGES]
    with open(os.path.join(ROOT, 'graph-data.js'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('window.GSOC_GRAPH = ' + json.dumps({'nodes': nodes, 'links': sorted(links)}) + ';\n')

    for slug, (meta, body, toc) in built.items():
        with open(os.path.join(ROOT, slug + '.html'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(page(slug, meta, body, toc))
        words = len(re.sub(r'<[^>]+>', ' ', body).split())
        print(f'{slug:16} {words:6} words  {len(toc):3} headings')


if __name__ == '__main__':
    main()
