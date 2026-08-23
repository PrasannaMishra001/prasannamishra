// Refreshes the statuses and the summary counts from the GitHub API so the tables do not go stale.
// If the request fails the page keeps the values it was published with.
(function () {
  var REPO = 'omegaup/omegaup';
  var AUTHOR = 'PrasannaMishra001';
  var SINCE = '2026-05-26';
  var CACHE_KEY = 'gsoc-pr-status-v2';
  var CACHE_MS = 30 * 60 * 1000;
  var MAX_PAGES = 3;
  var ENDPOINT = 'https://api.github.com/search/issues';
  var TYPE = { pull: 'pr', issues: 'issue' };

  if (!window.fetch || !window.Promise || !document.querySelectorAll) return;

  function isArray(v) { return Object.prototype.toString.call(v) === '[object Array]'; }
  function isInt(v) { return typeof v === 'number' && isFinite(v) && Math.floor(v) === v; }
  function isText(v) { return typeof v === 'string' && v.length > 0; }
  function size(map) { var n = 0, k; for (k in map) if (map.hasOwnProperty(k)) n++; return n; }
  function failure(kind, message) { var e = new Error(message || kind); e.kind = kind; return e; }

  function base(type) { return 'repo:' + REPO + '+author:' + AUTHOR + '+type:' + type; }

  function query(q, page) {
    var url = ENDPOINT + '?q=' + q + '&per_page=100&sort=created&order=desc&page=' + page;
    return fetch(url, { headers: { Accept: 'application/vnd.github+json' } }).then(function (r) {
      if (r.status === 403 || r.status === 429) throw failure('ratelimit', 'rate limited');
      if (!r.ok) throw failure('http', 'request failed: ' + r.status);
      return r.json();
    });
  }

  // Numbers the published HTML already shows, so extra pages are only fetched when one is missing.
  function wanted(kind) {
    var cells = document.querySelectorAll('[data-state-for^="' + kind + '/"]');
    var want = {};
    for (var i = 0; i < cells.length; i++) {
      want[String(cells[i].getAttribute('data-state-for')).slice(kind.length + 1)] = true;
    }
    return want;
  }

  function search(kind) {
    var want = wanted(kind);
    var items = [];
    function page(n) {
      return query(base(TYPE[kind]), n).then(function (data) {
        if (!data || !isArray(data.items)) throw failure('schema', 'unexpected response');
        items = items.concat(data.items);
        data.items.forEach(function (item) { delete want[String(item && item.number)]; });
        var total = isInt(data.total_count) ? data.total_count : items.length;
        if (n < MAX_PAGES && items.length < total && size(want)) return page(n + 1);
        return items;
      });
    }
    return page(1);
  }

  // One extra search instead of one review lookup per pull request; skipped when nothing is open.
  function approvals(prs) {
    var pending = prs.filter(function (p) { return p && p.state === 'open' && p.draft !== true; });
    if (!pending.length) return Promise.resolve({});
    return query(base('pr') + '+state:open+review:approved', 1).then(function (data) {
      var map = {};
      if (data && isArray(data.items)) {
        data.items.forEach(function (item) { if (item && isInt(item.number)) map[String(item.number)] = true; });
      }
      return map;
    }, function () { return {}; });
  }

  function prState(item, approved) {
    var pr = item.pull_request || {};
    if (pr.merged_at || pr.merged === true || item.merged_at) return 'merged';
    if (item.state === 'closed') return 'closed';
    if (item.state !== 'open') return null;
    if (item.draft === true || pr.draft === true) return 'draft';
    return approved[String(item.number)] ? 'approved' : 'in review';
  }

  function issueState(item) {
    if (item.state === 'open') return 'open';
    if (item.state !== 'closed') return null;
    if (item.state_reason === 'not_planned') return 'not planned';
    if (item.state_reason === 'completed') return 'completed';
    return 'closed';
  }

  function inPeriod(item) { return isText(item.created_at) && item.created_at >= SINCE; }

  function collect(prs, issues, approved) {
    var data = { at: Date.now(), states: {}, extras: [], counts: {} };
    var tally = { merged: 0, approved: 0, 'in review': 0, draft: 0, closed: 0 };
    var opened = 0, mergedInPeriod = 0;

    function record(kind, item, state) {
      var key = kind + '/' + item.number;
      if (state) data.states[key] = state;
      if (inPeriod(item) && !document.querySelector('[data-state-for="' + key + '"]')) {
        data.extras.push({ kind: kind, number: item.number, title: String(item.title || '') });
      }
    }

    prs.forEach(function (item) {
      if (!item || !isInt(item.number)) return;
      var state = prState(item, approved);
      var merged = (item.pull_request || {}).merged_at;
      if (isText(merged) && merged >= SINCE) mergedInPeriod++;
      if (inPeriod(item)) {
        opened++;
        if (state && tally.hasOwnProperty(state)) tally[state]++;
      }
      record('pull', item, state);
    });

    issues.forEach(function (item) {
      if (!item || !isInt(item.number)) return;
      record('issues', item, issueState(item));
    });

    data.counts.opened = opened;
    data.counts.merged = tally.merged;
    data.counts['merged-of-opened'] = tally.merged;
    data.counts['merged-in-period'] = mergedInPeriod;
    data.counts.approved = tally.approved;
    data.counts['in-review'] = tally['in review'];
    data.counts.draft = tally.draft;
    data.counts.closed = tally.closed;
    data.extras.sort(function (a, b) { return a.number - b.number; });
    return data;
  }

  function cacheRead() {
    try {
      var hit = JSON.parse(window.localStorage.getItem(CACHE_KEY));
      if (!hit || typeof hit !== 'object' || !isInt(hit.at)) return null;
      if (!hit.states || typeof hit.states !== 'object') return null;
      if (!hit.counts || typeof hit.counts !== 'object') hit.counts = {};
      if (!isArray(hit.extras)) hit.extras = [];
      var age = Date.now() - hit.at;
      hit.stale = !(age >= 0 && age < CACHE_MS);
      return hit;
    } catch (e) { return null; }
  }

  function cacheWrite(data) {
    try { window.localStorage.setItem(CACHE_KEY, JSON.stringify(data)); } catch (e) { /* private mode */ }
  }

  function fetchFresh() {
    return Promise.all([search('pull'), search('issues')]).then(function (found) {
      if (!found[0].length && !found[1].length) throw failure('empty', 'no results, repo or account may have moved');
      return approvals(found[0]).then(function (approved) {
        var data = collect(found[0], found[1], approved);
        cacheWrite(data);
        return data;
      });
    });
  }

  function stateClass(cell, state) {
    var kept = String(cell.className || '').replace(/\bpr-state[\w-]*/g, '').replace(/\s+/g, ' ').trim();
    return (kept ? kept + ' ' : '') + 'pr-state pr-state-' + state.replace(/ /g, '-');
  }

  function rowFor(kind) {
    var cell = document.querySelector('[data-state-for^="' + kind + '/"]');
    while (cell && cell.tagName !== 'TR') cell = cell.parentNode;
    return cell && cell.parentNode ? cell : null;
  }

  function addRow(entry) {
    var ref = rowFor(entry.kind);
    if (!ref) return null;
    var columns = ref.children.length;
    var stateAt = 0, linkAt = columns - 1, i;
    for (i = 0; i < columns; i++) {
      if (ref.children[i].getAttribute('data-state-for')) stateAt = i;
      if (ref.children[i].querySelector('a[href*="/' + entry.kind + '/"]')) linkAt = i;
    }
    var titleAt = stateAt - 1 !== linkAt && stateAt > 0 ? stateAt - 1 : -1;
    for (i = 0; titleAt < 0 && i < columns; i++) { if (i !== stateAt && i !== linkAt) titleAt = i; }
    var row = document.createElement('tr');
    for (i = 0; i < columns; i++) row.appendChild(document.createElement('td'));
    row.children[stateAt].setAttribute('data-state-for', entry.kind + '/' + entry.number);
    var link = document.createElement('a');
    link.href = 'https://github.com/' + REPO + '/' + entry.kind + '/' + entry.number;
    link.textContent = '#' + entry.number;
    row.children[linkAt].appendChild(link);
    if (titleAt >= 0) row.children[titleAt].textContent = entry.title;
    ref.parentNode.appendChild(row);
    return row;
  }

  // Everything is applied together and rolled back on error, so the page is never left half updated.
  function apply(data) {
    var undo = [];
    try {
      data.extras.forEach(function (entry) {
        if (!isInt(entry && entry.number) || !TYPE[entry.kind]) return;
        var row = addRow(entry);
        if (row) undo.push(function () { if (row.parentNode) row.parentNode.removeChild(row); });
      });
      Object.keys(data.states).forEach(function (key) {
        var state = data.states[key];
        if (!isText(state)) return;
        var cells = document.querySelectorAll('[data-state-for="' + key + '"]');
        for (var i = 0; i < cells.length; i++) {
          (function (cell) {
            var text = cell.textContent, cls = cell.className;
            undo.push(function () { cell.className = cls; cell.textContent = text; });
            cell.className = stateClass(cell, state);
            cell.textContent = state;
          })(cells[i]);
        }
      });
      Object.keys(data.counts).forEach(function (name) {
        var value = data.counts[name];
        if (!isInt(value)) return;
        var slots = document.querySelectorAll('[data-count="' + name + '"]');
        for (var i = 0; i < slots.length; i++) {
          (function (slot) {
            var text = slot.textContent;
            undo.push(function () { slot.textContent = text; });
            slot.textContent = String(value);
          })(slots[i]);
        }
      });
    } catch (e) {
      undo.reverse().forEach(function (step) { try { step(); } catch (ignored) { /* keep unwinding */ } });
      throw e;
    }
  }

  function anchorIn(top, mark) {
    if (!top) return null;
    var node = mark;
    while (node && node.parentNode && node.parentNode !== top) node = node.parentNode;
    return node && node.parentNode === top ? node : null;
  }

  function anchor() {
    var marks = document.querySelectorAll('[data-state-for], [data-count]');
    if (!marks.length) return null;
    var mark = marks[marks.length - 1];
    return anchorIn(document.querySelector('article'), mark) || anchorIn(document.body, mark);
  }

  function note(text) {
    var spot = anchor();
    if (!spot) return;
    var old = document.querySelector('p.status-note[data-live]');
    if (old && old.parentNode) old.parentNode.removeChild(old);
    var line = document.createElement('p');
    line.className = 'status-note';
    line.setAttribute('data-live', '');
    line.textContent = text;
    spot.parentNode.insertBefore(line, spot.nextSibling);
  }

  function checkedOn(at) {
    return 'Statuses above were checked against GitHub on ' +
      new Date(at).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' }) + '.';
  }

  function start() {
    var cached = cacheRead();
    if (cached && !cached.stale) {
      try { apply(cached); note(checkedOn(cached.at)); } catch (e) { warn(e); }
      return;
    }
    fetchFresh().then(function (data) {
      apply(data);
      note(checkedOn(data.at));
    }).catch(function (err) {
      warn(err);
      if (cached) {
        try { apply(cached); note(checkedOn(cached.at)); return; } catch (e) { warn(e); }
      }
      note(err && err.kind === 'ratelimit'
        ? 'Statuses above could not be checked against GitHub just now, because of its rate limit, so they are the ones this page was published with.'
        : 'Statuses above could not be checked against GitHub just now, so they are the ones this page was published with.');
    });
  }

  function warn(err) {
    if (window.console && console.warn) console.warn('status refresh skipped:', err && err.message);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
