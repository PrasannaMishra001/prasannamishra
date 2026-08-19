// Refreshes the status column from the GitHub API so the tables do not go stale.
// If the request fails the page keeps the values it was published with.
(function () {
  var REPO = 'omegaup/omegaup';
  var AUTHOR = 'PrasannaMishra001';
  var SINCE = '2026-05-26';
  var CACHE_KEY = 'gsoc-pr-status';
  var CACHE_MS = 30 * 60 * 1000;

  function search(type) {
    var q = 'repo:' + REPO + '+author:' + AUTHOR + '+type:' + type;
    var url = 'https://api.github.com/search/issues?q=' + q + '&per_page=100';
    return fetch(url, { headers: { Accept: 'application/vnd.github+json' } })
      .then(function (r) {
        if (!r.ok) throw new Error(type + ' request failed: ' + r.status);
        return r.json();
      })
      .then(function (data) { return data.items || []; });
  }

  function stateOf(item, type) {
    if (type === 'issues') return item.state;
    if (item.pull_request && item.pull_request.merged_at) return 'merged';
    if (item.state === 'closed') return 'closed';
    return item.draft ? 'draft' : 'open';
  }

  function load() {
    try {
      var hit = JSON.parse(localStorage.getItem(CACHE_KEY));
      if (hit && Date.now() - hit.at < CACHE_MS) return Promise.resolve(hit);
    } catch (e) { /* no usable cache */ }

    return Promise.all([search('pr'), search('issue')]).then(function (results) {
      var fresh = { at: Date.now(), states: {}, extras: [], counts: {} };
      var prs = results[0];
      fresh.counts.opened = prs.filter(function (p) { return p.created_at >= SINCE; }).length;
      fresh.counts['merged-of-opened'] = prs.filter(function (p) {
        return p.created_at >= SINCE && p.pull_request && p.pull_request.merged_at;
      }).length;
      fresh.counts['merged-in-period'] = prs.filter(function (p) {
        return p.pull_request && p.pull_request.merged_at && p.pull_request.merged_at >= SINCE;
      }).length;
      ['pull', 'issues'].forEach(function (kind, i) {
        results[i].forEach(function (item) {
          var key = kind + '/' + item.number;
          fresh.states[key] = stateOf(item, kind === 'pull' ? 'pr' : 'issues');
          if (item.created_at >= SINCE && !document.querySelector('[data-state-for="' + key + '"]')) {
            fresh.extras.push({ key: key, kind: kind, number: item.number, title: item.title });
          }
        });
      });
      try { localStorage.setItem(CACHE_KEY, JSON.stringify(fresh)); } catch (e) { /* private mode */ }
      return fresh;
    });
  }

  function tableFor(kind) {
    var tables = document.querySelectorAll('.table-container > table');
    for (var i = 0; i < tables.length; i++) {
      if (tables[i].querySelector('[data-state-for^="' + kind + '/"]')) return tables[i];
    }
    return null;
  }

  function addRow(entry) {
    var table = tableFor(entry.kind);
    if (!table) return;
    var link = '<a href="https://github.com/' + REPO + '/' + entry.kind + '/' + entry.number + '">#' + entry.number + '</a>';
    var row = document.createElement('tr');
    if (entry.kind === 'pull') {
      row.innerHTML = '<td></td><td></td><td data-state-for="' + entry.key + '"></td><td>' + link + '</td>';
      row.children[1].textContent = entry.title;
    } else {
      row.innerHTML = '<td>' + link + '</td><td></td><td data-state-for="' + entry.key + '"></td>';
      row.children[1].textContent = entry.title;
    }
    table.querySelector('tbody').appendChild(row);
  }

  function note(when) {
    var line = document.createElement('p');
    line.className = 'status-note';
    line.textContent = 'Statuses above were checked against GitHub on ' +
      when.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' }) + '.';
    var heading = document.querySelector('article h2');
    if (heading) heading.parentNode.insertBefore(line, heading);
  }

  load().then(function (data) {
    data.extras.forEach(addRow);
    Object.keys(data.counts || {}).forEach(function (name) {
      var slot = document.querySelector('[data-count="' + name + '"]');
      if (slot) slot.textContent = data.counts[name];
    });
    Object.keys(data.states).forEach(function (key) {
      var cell = document.querySelector('[data-state-for="' + key + '"]');
      if (cell) cell.textContent = data.states[key];
    });
    note(new Date(data.at));
  }).catch(function (err) {
    if (window.console) console.warn('status refresh skipped:', err.message);
  });
})();
