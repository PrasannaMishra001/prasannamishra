"""Draws every diagram and chart on the site as inline SVG.

Nothing here carries a colour. Each shape gets a class and quartz.css decides
what it looks like, which is how the same drawing works in both themes.
"""

import datetime
import html
import math

PR = 'https://github.com/omegaup/omegaup/pull/'


def esc(text):
    return html.escape(str(text), quote=True)


class Svg:
    def __init__(self, width, height, title, minw=None):
        self.w, self.h, self.title = width, height, title
        self.minw = minw if minw is not None else min(width, 720)
        self.out = []

    def raw(self, markup):
        self.out.append(markup)

    def text(self, x, y, value, cls='d-s', anchor='start', extra=''):
        self.out.append(
            f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"{extra}>{esc(value)}</text>')

    def box(self, x, y, w, h, title, sub=None, cls='', href=None, sub2=None, state=None):
        ink = ' on-ink' if 'ink' in cls else ''
        parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" class="d-box {cls}"/>']
        cx = x + w / 2
        lines = 1 + (1 if sub else 0) + (1 if sub2 else 0)
        top = y + h / 2 - (lines - 1) * 8 + 4.5
        parts.append(f'<text x="{cx}" y="{top}" class="d-t{ink}" text-anchor="middle">{esc(title)}</text>')
        if sub:
            attr = f' data-state-svg="{state}"' if state else ''
            parts.append(
                f'<text x="{cx}" y="{top + 16}" class="d-s{ink}" text-anchor="middle"{attr}>{esc(sub)}</text>')
        if sub2:
            parts.append(f'<text x="{cx}" y="{top + 31}" class="d-s{ink}" text-anchor="middle">{esc(sub2)}</text>')
        body = ''.join(parts)
        if href:
            body = f'<a href="{href}" class="d-link">{body}</a>'
        self.out.append(body)

    def group(self, x, y, w, h, label=None):
        self.out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="d-group"/>')
        if label:
            self.text(x + 12, y + 18, label, 'd-cap')

    def line(self, points, cls='', arrow=True, label=None, label_at=None, label_anchor='middle'):
        path = ' '.join(f'{x},{y}' for x, y in points)
        self.out.append(f'<polyline points="{path}" class="d-line {cls}" stroke-linejoin="round" stroke-linecap="round"/>')
        if arrow:
            (x1, y1), (x2, y2) = points[-2], points[-1]
            angle = math.atan2(y2 - y1, x2 - x1)
            size = 7
            a = (x2 - size * math.cos(angle - 0.42), y2 - size * math.sin(angle - 0.42))
            b = (x2 - size * math.cos(angle + 0.42), y2 - size * math.sin(angle + 0.42))
            head = 'key' if 'key' in cls else ''
            self.out.append(
                f'<polygon points="{x2},{y2} {a[0]:.1f},{a[1]:.1f} {b[0]:.1f},{b[1]:.1f}" class="d-head {head}"/>')
        if label:
            lx, ly = label_at if label_at else (
                (points[0][0] + points[1][0]) / 2, (points[0][1] + points[1][1]) / 2 - 6)
            self.text(lx, ly, label, 'd-note', label_anchor)

    def render(self):
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{esc(self.title)}" '
                f'style="--minw:{self.minw}px" xmlns="http://www.w3.org/2000/svg">'
                + ''.join(self.out) + '</svg>')


# ---------------------------------------------------------------- diagrams

def architecture():
    s = Svg(842, 420, 'How a cron job reaches the admin page', minw=700)
    cols = {'jobs': (2, 200), 'run': (232, 160), 'store': (422, 215), 'ui': (667, 173)}
    for key, label in (('jobs', 'scheduled jobs'), ('run', 'shared runner'), ('store', 'tables'),
                       ('ui', 'what an admin sees')):
        s.text(cols[key][0] + 2, 22, label, 'd-cap')

    jobs = [('update_ranks.py', 'every day, 08:19'), ('assign_badges.py', 'every day, 09:23'),
            ('aggregate_feedback.py', 'every day, 10:18'), ('build_problem_rec_model.py', 'Sundays, 04:00'),
            ('problem_health_check.py', 'every day, 05:35')]
    jx, jw = cols['jobs']
    rx, rw = cols['run']
    for i, (name, when) in enumerate(jobs):
        y = 40 + i * 54
        s.box(jx, y, jw, 44, name, when, 'soft')
        s.line([(jx + jw, y + 22), (rx, y + 22)])

    s.raw(f'<rect x="{rx}" y="40" width="{rw}" height="260" rx="6" class="d-box key"/>')
    s.text(rx + rw / 2, 66, 'lib/runner.py', 'd-t', 'middle')
    steps = ['is it enabled?', 'take the lock', 'write a running row', 'time each phase',
             'record the outcome', 'release the lock']
    for i, step in enumerate(steps):
        y = 102 + i * 32
        s.text(rx + 16, y, f'{i + 1}', 'd-num')
        s.text(rx + 32, y, step, 'd-s')

    sx, sw = cols['store']
    tables = [(40, 'Cron_Jobs', 'read: is this job switched on'),
              (94, 'Cron_Runs', 'written: one row per run'),
              (202, 'Recommendation_Model_Runs', 'how good each model was'),
              (256, 'Problem_Health_Checks', 'open and resolved findings')]
    ux, uw = cols['ui']
    bus = sx + sw + 15
    for y, name, sub in tables:
        s.box(sx, y, sw, 44, name, sub, 'tint')
        s.line([(rx + rw, y + 22), (sx, y + 22)])
        s.line([(sx + sw, y + 22), (bus, y + 22)], arrow=False)
    s.line([(bus, 62), (bus, 278)], arrow=False)
    s.line([(bus, 170), (ux, 170)])

    s.raw(f'<rect x="{ux}" y="40" width="{uw}" height="260" rx="6" class="d-box ink"/>')
    s.text(ux + uw / 2, 66, '/admin/crons', 'd-t on-ink', 'middle')
    s.text(ux + uw / 2, 83, 'system admins only', 'd-s on-ink', 'middle')
    for i, item in enumerate(['health of each job', 'every recent run', 'timing of each phase',
                              'the error, if it failed', 'problems needing attention',
                              'model quality', 'a rerun button']):
        s.text(ux + 14, 116 + i * 26, item, 'd-s on-ink')

    # the rerun loop along the bottom
    y = 340
    s.box(ux, y, uw, 44, 'apiRerunCron', 'only writes a row', 'soft')
    s.box(sx, y, sw, 44, 'Cron_Run_Requests', 'pending, picked, done, failed', 'tint')
    s.box(rx, y, rw, 44, 'cron_dispatcher.py', 'a fixed list of jobs', 'soft')
    mid = y + 22
    s.line([(ux + uw / 2, 300), (ux + uw / 2, y)], 'key dash')
    s.line([(ux, mid), (sx + sw, mid)], 'key dash')
    s.line([(sx, mid), (rx + rw, mid)], 'key dash')
    s.line([(rx, mid), (jx + jw / 2, mid), (jx + jw / 2, 304)], 'key dash')
    s.text(jx, y + 64, 'the rerun path: only the dispatcher starts a job', 'd-note')
    return s.render()


def runner():
    s = Svg(790, 214, 'What the shared runner does around every job', minw=680)
    steps = [('is it enabled?', 'Cron_Jobs.enabled'), ('take the lock', 'a database lock'),
             ('write a row', 'status running'), ('run the job', 'each phase timed'),
             ('record outcome', 'success or failure'), ('release lock', 'and close up')]
    w, gap, y = 118, 14, 40
    for i, (title, sub) in enumerate(steps):
        x = 6 + i * (w + gap)
        s.text(x + 2, y - 10, f'0{i + 1}', 'd-num')
        s.box(x, y, w, 56, title, sub, 'key' if i == 3 else 'soft')
        if i:
            s.line([(x - gap, y + 28), (x, y + 28)])
    for i, note in ((0, 'switched off:'), (1, 'already running:')):
        x = 6 + i * (w + gap) + w / 2
        s.line([(x, y + 56), (x, y + 92)], 'dash')
        s.text(x, y + 110, note, 'd-note', 'middle')
        s.text(x, y + 125, 'exit 0, no row', 'd-note', 'middle')
    x1 = 6 + 4 * (w + gap)
    x2 = 6 + 5 * (w + gap) + w
    s.line([(x1, y + 66), (x1, y + 76), (x2, y + 76), (x2, y + 66)], arrow=False)
    s.text((x1 + x2) / 2, y + 96, 'in a finally block, so these', 'd-note', 'middle')
    s.text((x1 + x2) / 2, y + 111, 'happen even if the job raises', 'd-note', 'middle')
    return s.render()


def rerun():
    s = Svg(800, 436, 'What happens when an admin presses rerun', minw=700)
    lanes = [('admin', 'the admin', 'in a browser'), ('api', 'apiRerunCron', 'PHP'),
             ('queue', 'Cron_Run_Requests', 'a table'), ('disp', 'cron_dispatcher.py', 'a trusted worker'),
             ('job', 'the job', 'via the runner')]
    xs = {}
    for i, (key, title, sub) in enumerate(lanes):
        cx = 80 + i * 160
        xs[key] = cx
        s.box(cx - 73, 8, 146, 46, title, sub, 'key' if key == 'disp' else 'soft')
        s.line([(cx, 54), (cx, 428)], 'dash', arrow=False)

    def msg(y, a, b, label, cls=''):
        s.line([(xs[a], y), (xs[b], y)], cls)
        s.text((xs[a] + xs[b]) / 2, y - 7, label, 'd-note', 'middle')

    msg(94, 'admin', 'api', 'rerun update_ranks.py')
    s.raw(f'<rect x="{xs["api"] - 70}" y="108" width="140" height="58" rx="5" class="d-box soft"/>')
    for i, t in enumerate(['a system admin?', 'known and enabled?', 'nothing queued?']):
        s.text(xs['api'], 125 + i * 15, t, 'd-s', 'middle')
    msg(196, 'api', 'queue', 'insert a pending row', 'key')
    msg(230, 'api', 'admin', 'queued', 'dash')
    msg(276, 'disp', 'queue', 'claim the row', 'key')
    msg(312, 'disp', 'job', 'start, with a timeout', 'key')
    msg(348, 'job', 'disp', 'exit code, stderr', 'dash')
    msg(384, 'disp', 'queue', 'done or failed, run id', 'key')
    s.line([(xs['disp'], 418), (xs['admin'], 418)], 'dash')
    s.text((xs['admin'] + xs['api']) / 2, 411, 'a notification', 'd-note', 'middle')
    return s.render()


def guardrail():
    s = Svg(800, 262, 'What decides whether a trained model is published', minw=700)
    y, h = 36, 60
    boxes = [(6, 126, 'train', 'on 80% of users', 'soft'),
             (150, 150, 'score it', 'MAP@3 on the rest', 'soft'),
             (318, 150, 'above the floor?', 'MAP at least 0.05', 'soft'),
             (486, 172, 'not much worse?', 'last published - 0.05', 'soft'),
             (676, 118, 'publish', 'write the file', 'ink')]
    for i, (x, w, title, sub, cls) in enumerate(boxes):
        s.box(x, y, w, h, title, sub, cls)
        if i:
            px, pw = boxes[i - 1][0], boxes[i - 1][1]
            s.line([(px + pw, y + h / 2), (x, y + h / 2)])
    s.box(318, 170, 340, 56, 'hold it back', 'old file stays, reason stored, exit 1', 'key')
    for x in (393, 572):
        s.line([(x, y + h), (x, 170)], 'dash')
        s.text(x + 8, 138, 'no', 'd-note')
    s.text(6, 190, 'every run writes a row to', 'd-note')
    s.text(6, 206, 'Recommendation_Model_Runs,', 'd-note')
    s.text(6, 222, 'published or not', 'd-note')
    return s.render()


def finding():
    s = Svg(810, 244, 'The life of one health finding', minw=700)
    y, h = 92, 60
    s.box(10, y, 160, h, 'nothing on record', 'this problem and check', 'soft')
    s.box(300, y, 220, h, 'open', 'first_detected_at is kept', 'key')
    s.box(650, y, 150, h, 'resolved', 'resolved_at is set', 'tint')
    s.line([(170, y + h / 2), (300, y + h / 2)], label='the check finds it')
    s.line([(520, y + h / 2), (650, y + h / 2)], label='a run misses it')
    s.line([(365, y), (365, 50), (455, 50), (455, y)])
    s.text(410, 38, 'seen again: only last_seen_at moves', 'd-note', 'middle')
    s.line([(725, y + h), (725, 198), (410, 198), (410, y + h)])
    s.text(568, 218, 'it comes back: reopened, first_detected_at starts again', 'd-note', 'middle')
    return s.render()


def stack(prs):
    """The control plane as it merged. Each box is a pull request."""
    s = Svg(800, 424, 'The control plane pull requests and the order they depend on each other', minw=700)
    w, h, gap = 104, 60, 10

    def col(c):
        return 6 + (c - 1) * (w + gap)

    def node(c, y, number, name):
        pr = prs.get(number, {})
        if pr.get('merged'):
            date = datetime.date.fromisoformat(pr['merged'])
            sub, cls = f'merged {date.day} {date.strftime("%b")}', 'tint'
        elif pr.get('closed'):
            sub, cls = 'closed', 'soft'
        else:
            sub, cls = 'open', 'soft open'
        s.box(col(c), y, w, h, f'#{number}', name, cls, href=PR + str(number), sub2=sub)

    rows = {'php': 34, 'py': 148, 'guard': 232, 'rerun': 354}
    s.text(6, 20, 'php and the page', 'd-cap')
    for c, n, name in ((1, 9995, 'tables'), (2, 9996, 'data access'), (3, 10000, 'admin api'), (6, 10008, 'dashboard')):
        node(c, rows['php'], n, name)
    y = rows['php'] + h / 2
    s.line([(col(1) + w, y), (col(2), y)])
    s.line([(col(2) + w, y), (col(3), y)])
    s.line([(col(3) + w, y), (col(6), y)])

    s.text(col(2), rows['py'] - 12, 'python', 'd-cap')
    for c, n, name in ((2, 9998, 'runner'), (3, 10003, 'update_ranks'), (4, 10009, 'two more jobs'),
                       (5, 10022, 'the last two')):
        node(c, rows['py'], n, name)
    y = rows['py'] + h / 2
    s.line([(col(1) + w / 2, rows['php'] + h), (col(1) + w / 2, y), (col(2), y)])
    for c in (2, 3, 4):
        s.line([(col(c) + w, y), (col(c + 1), y)])
    node(3, rows['guard'], 10011, 'ranking audit')
    s.line([(col(3) + w / 2, rows['py'] + h), (col(3) + w / 2, rows['guard'])])

    s.text(col(2), rows['rerun'] - 12, 'rerun, then the second pass on the page', 'd-cap')
    chain = [(10155, 'request table'), (10156, 'request dao'), (10275, 'rerun api'), (10021, 'dispatcher'),
             (10276, 'rerun button'), (10277, 'cypress'), (10048, 'dashboard v2')]
    for i, (n, name) in enumerate(chain):
        node(i + 1, rows['rerun'], n, name)
        if i:
            yy = rows['rerun'] + h / 2
            s.line([(col(i) + w, yy), (col(i + 1), yy)])
    x = col(6) + w / 2
    s.line([(x, rows['php'] + h), (x, 316), (col(1) + w / 2, 316), (col(1) + w / 2, rows['rerun'])])
    return s.render()


# ------------------------------------------------------------------ charts

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def monthly(prs, today):
    """Pull requests opened and merged in each month."""
    first = (2025, 8)
    last = (today.year, today.month)
    months = []
    y, m = first
    while (y, m) <= last:
        months.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    opened = {k: 0 for k in months}
    merged = {k: 0 for k in months}
    for pr in prs:
        k = tuple(int(v) for v in pr['created'].split('-')[:2])
        opened[k] = opened.get(k, 0) + 1
        if pr['merged']:
            k = tuple(int(v) for v in pr['merged'].split('-')[:2])
            merged[k] = merged.get(k, 0) + 1

    w, h = 800, 290
    left, right, top, bottom = 34, 10, 22, 46
    plot_w, plot_h = w - left - right, h - top - bottom
    peak = max(max(opened.values()), max(merged.values()))
    ceil = int(math.ceil(peak / 10.0)) * 10
    s = Svg(w, h, 'Pull requests opened and merged in each month', minw=600)
    for tick in range(0, ceil + 1, 10):
        yy = top + plot_h - plot_h * tick / ceil
        s.raw(f'<line x1="{left}" y1="{yy}" x2="{w - right}" y2="{yy}" class="c-grid"/>')
        s.text(left - 8, yy + 3.5, tick, 'c-axis', 'end')
    band = plot_w / len(months)
    bar = min(16, band * 0.3)

    # the coding period, 26 May to 24 August 2026
    def at(year, month, day):
        index = months.index((year, month))
        return left + band * (index + (day - 1) / 31.0)
    if (2026, 8) in months:
        x1, x2 = at(2026, 5, 26), at(2026, 8, 24)
        s.raw(f'<rect x="{x1:.1f}" y="{top}" width="{x2 - x1:.1f}" height="{plot_h}" class="c-band"/>')
        s.text((x1 + x2) / 2, top - 7, 'coding period', 'c-axis', 'middle')

    rows = []
    for i, key in enumerate(months):
        cx = left + band * (i + 0.5)
        name = f'{MONTHS[key[1] - 1]} {key[0]}'
        tip = f'{name}\n{opened[key]} opened\n{merged[key]} merged'
        rows.append((name, opened[key], merged[key]))
        for value, cls, dx in ((opened[key], 'c-a', -bar - 1), (merged[key], 'c-b', 1)):
            bh = plot_h * value / ceil
            if value:
                yy = top + plot_h - bh
                r = min(4, bh)
                x = cx + dx
                s.raw(f'<path d="M{x:.1f},{top + plot_h} V{yy + r:.1f} Q{x:.1f},{yy:.1f} {x + r:.1f},{yy:.1f} '
                      f'H{x + bar - r:.1f} Q{x + bar:.1f},{yy:.1f} {x + bar:.1f},{yy + r:.1f} V{top + plot_h} Z" '
                      f'class="c-mark {cls}" data-mark="m{i}"/>')
        s.raw(f'<rect x="{left + band * i:.1f}" y="{top}" width="{band:.1f}" height="{plot_h}" class="c-hit" '
              f'data-mark="m{i}" data-tip="{esc(tip)}"/>')
        s.text(cx, h - bottom + 16, MONTHS[key[1] - 1], 'c-axis', 'middle')
        if key[1] == 1 or i == 0:
            s.text(cx, h - bottom + 31, key[0], 'c-axis', 'middle')
    busiest = max(months, key=lambda k: opened[k])
    i = months.index(busiest)
    s.text(left + band * (i + 0.5) - bar / 2 - 1, top + plot_h - plot_h * opened[busiest] / ceil - 6,
           opened[busiest], 'c-val', 'middle')
    return s.render(), rows


def waiting(prs, names, today, start=datetime.date(2026, 5, 26)):
    """One bar per pull request, from the day it was opened to the day it merged."""
    rows = [p for p in prs if p['created'] >= start.isoformat()]
    rows.sort(key=lambda p: (p['created'], p['number']))
    label_w, row_h, top = 206, 15, 30
    w = 800
    right = 14
    plot_w = w - label_w - right
    h = top + row_h * len(rows) + 30
    span = (today - start).days + 2
    s = Svg(w, h, 'How long each pull request waited between being opened and being merged', minw=640)

    def x_of(day):
        return label_w + plot_w * (day - start).days / span

    # month gridlines
    d = datetime.date(start.year, start.month, 1)
    while d <= today:
        if d >= start:
            x = x_of(d)
            s.raw(f'<line x1="{x:.1f}" y1="{top - 4}" x2="{x:.1f}" y2="{h - 26}" class="c-grid"/>')
            s.text(x + 4, top - 10, MONTHS[d.month - 1], 'c-axis')
        d = datetime.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    end = datetime.date(2026, 8, 24)
    s.raw(f'<rect x="{x_of(start):.1f}" y="{top - 4}" width="{x_of(end) - x_of(start):.1f}" '
          f'height="{h - 22 - top}" class="c-band"/>')
    s.text(x_of(end) - 4, h - 8, 'coding period ends, 24 Aug', 'c-axis', 'end')
    table = []
    for i, pr in enumerate(rows):
        y = top + i * row_h
        opened = datetime.date.fromisoformat(pr['created'])
        if pr['merged']:
            stop, cls, word = datetime.date.fromisoformat(pr['merged']), 'c-b', 'merged'
        elif pr['closed']:
            stop, cls, word = datetime.date.fromisoformat(pr['closed']), 'c-wait', 'closed, not merged'
        else:
            stop, cls, word = today, 'c-open', 'still open'
        days = (stop - opened).days
        x1, x2 = x_of(opened), max(x_of(stop), x_of(opened) + 4)
        name = names.get(pr['number'], pr['title'])
        tip = f"#{pr['number']} {name}\nopened {opened.day} {MONTHS[opened.month - 1]}\n{word} after {days} days"
        table.append((pr['number'], name, pr['created'], word, days))
        s.raw(f'<a href="{PR}{pr["number"]}" class="d-link">'
              f'<text x="{label_w - 10}" y="{y + 10.5}" class="c-label" text-anchor="end">'
              f'{esc(name)} <tspan class="c-label dim">#{pr["number"]}</tspan></text></a>')
        s.raw(f'<rect x="{x1:.1f}" y="{y + 3}" width="{x2 - x1:.1f}" height="9" rx="3" class="c-mark {cls}" '
              f'data-mark="w{i}"/>')
        s.raw(f'<rect x="{label_w}" y="{y}" width="{plot_w}" height="{row_h}" class="c-hit" data-mark="w{i}" '
              f'data-tip="{esc(tip)}"/>')
    return s.render(), table
