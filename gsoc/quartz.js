(function () {
  'use strict';

  var NS = 'http://www.w3.org/2000/svg';
  var root = document.documentElement;
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }
  function svgEl(tag, attrs) {
    var node = document.createElementNS(NS, tag);
    for (var k in attrs) node.setAttribute(k, attrs[k]);
    return node;
  }
  function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }

  var ICON = {
    expand: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    prev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>',
    next: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>'
  };

  /* ---------- theme ---------- */
  function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    try { localStorage.setItem('gsoc-theme', theme); } catch (e) { /* private mode */ }
    var meta = $('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#161618' : '#faf8f8');
  }

  // The new theme is painted on top of the old one and revealed through a
  // circle that grows out of the button, so it spreads like a drop of ink.
  function toggleTheme(button) {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    button.classList.remove('rippling');
    void button.offsetWidth;
    button.classList.add('rippling');
    if (!document.startViewTransition || reduced) { setTheme(next); return; }
    var box = button.getBoundingClientRect();
    var x = box.left + box.width / 2, y = box.top + box.height / 2;
    var radius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));
    var transition = document.startViewTransition(function () { setTheme(next); });
    transition.ready.then(function () {
      root.animate(
        { clipPath: ['circle(0px at ' + x + 'px ' + y + 'px)', 'circle(' + radius + 'px at ' + x + 'px ' + y + 'px)'] },
        { duration: 750, easing: 'cubic-bezier(0.22, 0.61, 0.36, 1)', pseudoElement: '::view-transition-new(root)' }
      );
    }).catch(function () { /* the theme is already applied */ });
  }

  /* ---------- folds, table of contents, progress ---------- */
  function initFolds() {
    $$('[data-fold]').forEach(function (button) {
      var target = document.getElementById(button.dataset.fold);
      if (!target) return;
      button.addEventListener('click', function () {
        button.classList.toggle('collapsed');
        target.classList.toggle('collapsed');
      });
    });
    var active = $('.explorer-content a.active');
    var list = $('.explorer-ul');
    if (active && list) {
      var a = active.getBoundingClientRect(), l = list.getBoundingClientRect();
      if (a.bottom > l.bottom - 8) list.scrollTop += a.bottom - l.bottom + 40;
    }
  }

  function initToc() {
    var links = $$('.toc-content a');
    var headings = links
      .map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); })
      .filter(Boolean);
    if (!headings.length) return;
    var visible = {};
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) { visible[entry.target.id] = entry.isIntersecting; });
      var current = null;
      for (var i = 0; i < headings.length; i++) if (visible[headings[i].id]) { current = headings[i].id; break; }
      if (!current) return;
      links.forEach(function (a) { a.classList.toggle('in-view', a.getAttribute('href') === '#' + current); });
    }, { rootMargin: '-8% 0px -72% 0px' });
    headings.forEach(function (h) { observer.observe(h); });
  }

  function initProgress() {
    var bar = $('.progress > i');
    if (!bar) return;
    var queued = false;
    function paint() {
      queued = false;
      var max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = 'scaleX(' + (max > 0 ? clamp(window.scrollY / max, 0, 1) : 0) + ')';
    }
    window.addEventListener('scroll', function () { if (!queued) { queued = true; requestAnimationFrame(paint); } }, { passive: true });
    paint();
  }

  function initReveal() {
    var items = $$('.reveal');
    if (!items.length) return;
    if (reduced || !window.IntersectionObserver) { items.forEach(function (n) { n.classList.add('is-in'); }); return; }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add('is-in'); observer.unobserve(entry.target); }
      });
    }, { rootMargin: '0px 0px -6% 0px' });
    items.forEach(function (n) { observer.observe(n); });
  }

  /* ---------- code blocks ---------- */
  function initCode() {
    $$('.codeblock').forEach(function (block) {
      var button = $('button', block);
      var code = $('pre', block);
      if (!button || !code) return;
      button.addEventListener('click', function () {
        var done = function () {
          button.textContent = 'copied';
          setTimeout(function () { button.textContent = 'copy'; }, 1400);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(code.innerText).then(done, function () {});
      });
    });
  }

  /* ---------- tooltips for charts ---------- */
  function initTips() {
    var marks = $$('[data-tip]');
    if (!marks.length) return;
    var tip = el('div', 'tip');
    document.body.appendChild(tip);
    function place(event) {
      var x = event.clientX + 14, y = event.clientY + 16;
      var box = tip.getBoundingClientRect();
      if (x + box.width > window.innerWidth - 8) x = event.clientX - box.width - 14;
      if (y + box.height > window.innerHeight - 8) y = event.clientY - box.height - 12;
      tip.style.left = Math.max(8, x) + 'px';
      tip.style.top = Math.max(8, y) + 'px';
    }
    marks.forEach(function (mark) {
      var svg = mark.ownerSVGElement;
      var group = mark.getAttribute('data-mark');
      mark.addEventListener('pointerenter', function (event) {
        tip.textContent = mark.getAttribute('data-tip');
        tip.classList.add('show');
        place(event);
        if (svg && group) {
          svg.classList.add('hovering');
          $$('[data-mark="' + group + '"]', svg).forEach(function (m) { m.classList.add('is-hover'); });
        }
      });
      mark.addEventListener('pointermove', place);
      mark.addEventListener('pointerleave', function () {
        tip.classList.remove('show');
        if (svg) {
          svg.classList.remove('hovering');
          $$('.is-hover', svg).forEach(function (m) { m.classList.remove('is-hover'); });
        }
      });
    });
  }

  /* ---------- filter above the long tables ---------- */
  function initFilters() {
    $$('.filter').forEach(function (bar) {
      var table = document.getElementById(bar.dataset.for);
      if (!table) return;
      var input = $('input', bar);
      var buttons = $$('button[data-state]', bar);
      var count = $('.count', bar);
      var rows = $$('tbody tr', table);
      var state = '';
      function apply() {
        var q = (input.value || '').trim().toLowerCase();
        var shown = 0, lastGroup = null, groupHas = false;
        rows.forEach(function (row) {
          if (row.classList.contains('group-row')) {
            if (lastGroup) lastGroup.hidden = !groupHas;
            lastGroup = row; groupHas = false;
            return;
          }
          var cell = $('[data-state-for]', row);
          var s = cell ? cell.textContent.trim() : '';
          var ok = (!q || row.textContent.toLowerCase().indexOf(q) !== -1) &&
            (!state || state.split('|').indexOf(s) !== -1);
          row.hidden = !ok;
          if (ok) { shown++; groupHas = true; }
        });
        if (lastGroup) lastGroup.hidden = !groupHas;
        if (count) count.textContent = shown + ' shown';
      }
      input.addEventListener('input', apply);
      buttons.forEach(function (button) {
        button.addEventListener('click', function () {
          var on = button.getAttribute('aria-pressed') === 'true';
          buttons.forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
          button.setAttribute('aria-pressed', on ? 'false' : 'true');
          state = on ? '' : button.dataset.state;
          apply();
        });
      });
      // The statuses are refreshed from GitHub after load, so the filter is applied again then.
      document.addEventListener('gsoc:status', apply);
      apply();
    });
  }

  /* ---------- pan and zoom ---------- */
  // Wheel zooms around the pointer, dragging pans, two fingers pinch.
  function panZoom(stage, item, opts) {
    var state = { x: 0, y: 0, k: 1 };
    var min = (opts && opts.min) || 0.2, max = (opts && opts.max) || 8;
    var pointers = {}, last = null, pinch = 0;
    function paint() { item.style.transform = 'translate(' + state.x + 'px,' + state.y + 'px) scale(' + state.k + ')'; }
    function zoomAt(cx, cy, factor) {
      var k = clamp(state.k * factor, min, max);
      var box = stage.getBoundingClientRect();
      var px = cx - box.left, py = cy - box.top;
      state.x = px - (px - state.x) * (k / state.k);
      state.y = py - (py - state.y) * (k / state.k);
      state.k = k;
      paint();
    }
    function fit(w, h, pad) {
      var box = stage.getBoundingClientRect();
      pad = pad == null ? 48 : pad;
      var k = Math.min((box.width - pad * 2) / w, (box.height - pad * 2 - 40) / h, opts && opts.fitMax || 1.6);
      min = Math.min(min, k * 0.5);
      state.k = k;
      state.x = (box.width - w * k) / 2;
      state.y = (box.height - 40 - h * k) / 2;
      paint();
    }
    stage.addEventListener('wheel', function (event) {
      event.preventDefault();
      zoomAt(event.clientX, event.clientY, Math.exp(-event.deltaY * (event.ctrlKey ? 0.01 : 0.0018)));
    }, { passive: false });
    stage.addEventListener('pointerdown', function (event) {
      if (event.target.closest && event.target.closest('.viewer-bar, .viewer-close')) return;
      pointers[event.pointerId] = { x: event.clientX, y: event.clientY };
      last = { x: event.clientX, y: event.clientY };
      stage.setPointerCapture(event.pointerId);
      stage.classList.add('dragging');
      var ids = Object.keys(pointers);
      if (ids.length === 2) pinch = Math.hypot(pointers[ids[0]].x - pointers[ids[1]].x, pointers[ids[0]].y - pointers[ids[1]].y);
    });
    stage.addEventListener('pointermove', function (event) {
      if (!pointers[event.pointerId]) return;
      pointers[event.pointerId] = { x: event.clientX, y: event.clientY };
      var ids = Object.keys(pointers);
      if (ids.length === 2) {
        var a = pointers[ids[0]], b = pointers[ids[1]];
        var d = Math.hypot(a.x - b.x, a.y - b.y);
        if (pinch) zoomAt((a.x + b.x) / 2, (a.y + b.y) / 2, d / pinch);
        pinch = d;
        return;
      }
      state.x += event.clientX - last.x;
      state.y += event.clientY - last.y;
      last = { x: event.clientX, y: event.clientY };
      paint();
    });
    function release(event) {
      delete pointers[event.pointerId];
      pinch = 0;
      if (!Object.keys(pointers).length) stage.classList.remove('dragging');
    }
    stage.addEventListener('pointerup', release);
    stage.addEventListener('pointercancel', release);
    return { fit: fit, zoomBy: function (f) { var b = stage.getBoundingClientRect(); zoomAt(b.left + b.width / 2, b.top + b.height / 2, f); } };
  }

  /* ---------- viewer for images and diagrams ---------- */
  var viewer = null;
  function buildViewer() {
    var wrap = el('div', 'viewer');
    wrap.setAttribute('role', 'dialog');
    wrap.setAttribute('aria-modal', 'true');
    wrap.innerHTML =
      '<div class="viewer-stage"><div class="viewer-item"></div></div>' +
      '<button type="button" class="icon-btn viewer-close" aria-label="Close">' + ICON.close + '</button>' +
      '<div class="viewer-bar">' +
        '<button type="button" class="icon-btn" data-act="prev" aria-label="Previous">' + ICON.prev + '</button>' +
        '<button type="button" class="icon-btn" data-act="out" aria-label="Zoom out">&minus;</button>' +
        '<button type="button" class="icon-btn" data-act="fit" aria-label="Fit">1:1</button>' +
        '<button type="button" class="icon-btn" data-act="in" aria-label="Zoom in">+</button>' +
        '<button type="button" class="icon-btn" data-act="next" aria-label="Next">' + ICON.next + '</button>' +
        '<span class="cap"></span>' +
      '</div>';
    document.body.appendChild(wrap);
    var stage = $('.viewer-stage', wrap), item = $('.viewer-item', wrap);
    var pz = panZoom(stage, item, { fitMax: 2.2 });
    var api = { wrap: wrap, item: item, pz: pz, list: [], at: 0, size: [1, 1], back: null };

    function close() {
      wrap.classList.remove('open');
      item.innerHTML = '';
      document.body.style.overflow = '';
      if (api.back) api.back.focus();
    }
    api.close = close;
    $('.viewer-close', wrap).addEventListener('click', close);
    stage.addEventListener('dblclick', function () { pz.fit(api.size[0], api.size[1]); });
    stage.addEventListener('click', function (event) { if (event.target === stage) close(); });
    $('.viewer-bar', wrap).addEventListener('click', function (event) {
      var button = event.target.closest('button');
      if (!button) return;
      var act = button.dataset.act;
      if (act === 'in') pz.zoomBy(1.35);
      if (act === 'out') pz.zoomBy(1 / 1.35);
      if (act === 'fit') pz.fit(api.size[0], api.size[1]);
      if (act === 'prev') api.show(api.at - 1);
      if (act === 'next') api.show(api.at + 1);
    });
    document.addEventListener('keydown', function (event) {
      if (!wrap.classList.contains('open')) return;
      if (event.key === 'Escape') close();
      if (event.key === 'ArrowLeft') api.show(api.at - 1);
      if (event.key === 'ArrowRight') api.show(api.at + 1);
      if (event.key === '+' || event.key === '=') pz.zoomBy(1.35);
      if (event.key === '-') pz.zoomBy(1 / 1.35);
    });

    api.show = function (index) {
      if (!api.list.length) return;
      api.at = (index + api.list.length) % api.list.length;
      var entry = api.list[api.at];
      item.innerHTML = '';
      $('.cap', wrap).textContent = entry.caption || '';
      var many = api.list.length > 1;
      $('[data-act="prev"]', wrap).style.display = many ? '' : 'none';
      $('[data-act="next"]', wrap).style.display = many ? '' : 'none';
      if (entry.svg) {
        var copy = entry.svg.cloneNode(true);
        var vb = (entry.svg.getAttribute('viewBox') || '0 0 800 400').split(/\s+/).map(Number);
        copy.setAttribute('width', vb[2]);
        copy.setAttribute('height', vb[3]);
        copy.style.padding = '18px';
        copy.style.boxSizing = 'content-box';
        copy.style.width = vb[2] + 'px';
        copy.style.minWidth = '0';
        item.appendChild(copy);
        api.size = [vb[2] + 36, vb[3] + 36];
        pz.fit(api.size[0], api.size[1]);
        return;
      }
      var img = new Image();
      img.alt = entry.caption || '';
      img.onload = function () {
        if (api.list[api.at] !== entry) return;
        img.style.width = img.naturalWidth + 'px';
        api.size = [img.naturalWidth, img.naturalHeight];
        item.appendChild(img);
        pz.fit(api.size[0], api.size[1]);
      };
      img.src = entry.src;
    };
    api.open = function (list, index, back) {
      api.list = list; api.back = back || null;
      wrap.classList.add('open');
      document.body.style.overflow = 'hidden';
      api.show(index || 0);
    };
    return api;
  }

  function captionOf(figure) {
    var cap = figure && $('figcaption', figure);
    if (cap) return cap.textContent.trim();
    var img = figure && $('img', figure);
    return img ? img.alt : '';
  }

  function initViewer() {
    var figures = $$('figure.zoomable');
    figures.forEach(function (figure) {
      var img = $('img', figure);
      if (!img) return;
      img.setAttribute('tabindex', '0');
      function open() {
        viewer = viewer || buildViewer();
        var scope = figure.closest('.gallery, .fig-row');
        var group = scope ? $$('figure.zoomable', scope) : [figure];
        var list = group.map(function (f) {
          var i = $('img', f);
          return { src: i.getAttribute('data-full') || i.currentSrc || i.src, caption: captionOf(f) };
        });
        viewer.open(list, group.indexOf(figure), img);
      }
      img.addEventListener('click', open);
      img.addEventListener('keydown', function (event) { if (event.key === 'Enter') open(); });
    });

    $$('.diagram').forEach(function (diagram) {
      var svg = $('.diagram-body svg', diagram);
      if (!svg) return;
      var tools = el('div', 'diagram-tools');
      var button = el('button', 'icon-btn');
      button.type = 'button';
      button.setAttribute('aria-label', 'Open larger, with zoom');
      button.title = 'Open larger, with zoom';
      button.innerHTML = ICON.expand;
      tools.appendChild(button);
      diagram.appendChild(tools);
      function open() {
        viewer = viewer || buildViewer();
        viewer.open([{ svg: svg, caption: captionOf(diagram) }], 0, button);
      }
      button.addEventListener('click', open);
      svg.addEventListener('dblclick', open);
    });
  }

  /* ---------- graph ---------- */
  // A small force layout. Every node repels every other, links act as springs,
  // and the pointer is a magnet: nodes near it lean towards it, and let go
  // again when it leaves. Dragging a node moves it and the rest follow.
  function drawGraph(container, data, opts) {
    opts = opts || {};
    var current = opts.current;
    var byId = {};
    var nodes = data.nodes.map(function (n) {
      var node = { id: n.id, href: n.href, label: n.label, kind: n.kind, x: 0, y: 0, vx: 0, vy: 0, links: 0 };
      byId[n.id] = node;
      return node;
    });
    var links = data.links
      .filter(function (l) { return byId[l[0]] && byId[l[1]]; })
      .map(function (l) { byId[l[0]].links++; byId[l[1]].links++; return { a: byId[l[0]], b: byId[l[1]] }; });

    var box = container.getBoundingClientRect();
    var w = Math.max(220, Math.round(box.width)), h = Math.max(220, Math.round(box.height));
    var cx = w / 2, cy = h / 2;
    var big = !!opts.big;
    var crowded = nodes.length > 8;
    var rest = big ? Math.min(w, h) * 0.3 : Math.min(w, h) * (crowded ? 0.36 : 0.34);
    var charge = big ? 30000 : (crowded ? 3200 : 3000);
    var squash = big ? 1.6 : 2.2;
    var gravity = big ? 0.005 : 0.012;

    container.innerHTML = '';
    // With many nodes the names collide, so only the important ones stay
    // visible and the rest appear as the pointer comes near.
    var shy = crowded && !big;
    var svg = svgEl('svg', { width: '100%', height: '100%', viewBox: '0 0 ' + w + ' ' + h });
    if (shy) svg.setAttribute('class', 'is-shy');
    var world = svgEl('g', {});
    svg.appendChild(world);

    nodes.forEach(function (n, i) {
      var angle = (2 * Math.PI * i) / nodes.length;
      var r = n.id === current ? 0 : rest * (0.8 + (i % 3) * 0.25);
      n.x = cx + r * Math.cos(angle);
      n.y = cy + r * Math.sin(angle);
      n.r = (big ? 5 : 4) + Math.min(big ? 5 : 3.5, Math.sqrt(n.links) * (big ? 1.3 : 0.9)) + (n.id === current ? 1.5 : 0);
      // Half the width of the label, so a node near the edge keeps its name inside the box.
      n.half = Math.min(w / 2 - 6, n.label.length * 3.05 + 4);
    });

    var edges = links.map(function (l) {
      var line = svgEl('line', { 'class': 'graph-edge' });
      world.appendChild(line);
      l.el = line;
      return line;
    });

    nodes.forEach(function (n) {
      var g = svgEl('a', { 'class': 'graph-node is-kind-' + (n.kind || 'page') + (n.id === current ? ' is-current' : ''), href: n.href });
      n.circle = svgEl('circle', { r: n.r });
      n.text = svgEl('text', { 'text-anchor': 'middle', 'class': 'node-label' });
      n.text.textContent = n.label;
      g.appendChild(n.circle);
      g.appendChild(n.text);
      n.el = g;
      world.appendChild(g);
    });

    var view = { x: 0, y: 0, k: 1 };
    function paintView() { world.setAttribute('transform', 'translate(' + view.x + ' ' + view.y + ') scale(' + view.k + ')'); }

    function paint() {
      links.forEach(function (l) {
        l.el.setAttribute('x1', l.a.x); l.el.setAttribute('y1', l.a.y);
        l.el.setAttribute('x2', l.b.x); l.el.setAttribute('y2', l.b.y);
      });
      nodes.forEach(function (n) {
        n.circle.setAttribute('cx', n.x); n.circle.setAttribute('cy', n.y);
        n.text.setAttribute('x', n.x); n.text.setAttribute('y', n.y + n.r + 13);
      });
    }

    var dragging = null, magnet = null, frame = null, idle = 0;

    function tick() {
      var i, j, a, b, dx, dy, d, f;
      for (i = 0; i < nodes.length; i++) {
        for (j = i + 1; j < nodes.length; j++) {
          a = nodes[i]; b = nodes[j];
          dx = b.x - a.x; dy = b.y - a.y;
          // Labels are much wider than they are tall, so two nodes side by side
          // push apart harder than two stacked ones.
          var ex = dx / squash;
          d = Math.sqrt(ex * ex + dy * dy) || 0.01;
          f = charge / (d * d);
          a.vx -= (ex / d) * f; a.vy -= (dy / d) * f;
          b.vx += (ex / d) * f; b.vy += (dy / d) * f;
        }
      }
      links.forEach(function (l) {
        dx = l.b.x - l.a.x; dy = l.b.y - l.a.y;
        d = Math.sqrt(dx * dx + dy * dy) || 0.01;
        f = (d - rest) * 0.03;
        l.a.vx += (dx / d) * f; l.a.vy += (dy / d) * f;
        l.b.vx -= (dx / d) * f; l.b.vy -= (dy / d) * f;
      });
      var moved = 0;
      nodes.forEach(function (n) {
        n.vx += (cx - n.x) * gravity; n.vy += (cy - n.y) * gravity * (w / h);
        if (shy) n.el.classList.toggle('show-label', !!magnet && Math.hypot(magnet.x - n.x, magnet.y - n.y) < 78);
        if (magnet && n !== dragging) {
          dx = magnet.x - n.x; dy = magnet.y - n.y;
          d = Math.sqrt(dx * dx + dy * dy) || 0.01;
          var reach = big ? 170 : 110;
          if (d < reach) {
            var pull = (1 - d / reach);
            n.vx += dx * pull * 0.085; n.vy += dy * pull * 0.085;
          }
        }
        if (n === dragging) { n.vx = 0; n.vy = 0; return; }
        n.vx *= 0.82; n.vy *= 0.82;
        n.x += n.vx; n.y += n.vy;
        if (!big) {
          n.x = clamp(n.x, n.half, w - n.half);
          n.y = clamp(n.y, 14, h - 46);
        }
        moved += Math.abs(n.vx) + Math.abs(n.vy);
      });
      paint();
      return moved;
    }

    function run() {
      frame = null;
      var moved = tick();
      idle = moved < 0.1 && !dragging && !magnet ? idle + 1 : 0;
      if (idle < 30) frame = requestAnimationFrame(run);
    }
    function wake() { idle = 0; if (!frame) frame = requestAnimationFrame(run); }

    function toWorld(event) {
      var rect = svg.getBoundingClientRect();
      var sx = (event.clientX - rect.left) * (w / rect.width);
      var sy = (event.clientY - rect.top) * (h / rect.height);
      return { x: (sx - view.x) / view.k, y: (sy - view.y) / view.k };
    }

    function focus(node, on) {
      svg.classList.toggle('has-focus', on);
      nodes.forEach(function (n) { n.el.classList.remove('is-focus', 'is-near'); });
      links.forEach(function (l) { l.el.classList.remove('is-focus'); });
      if (!on) return;
      node.el.classList.add('is-focus');
      links.forEach(function (l) {
        if (l.a === node || l.b === node) {
          l.el.classList.add('is-focus');
          (l.a === node ? l.b : l.a).el.classList.add('is-near');
        }
      });
    }

    svg.addEventListener('pointermove', function (event) {
      if (pan) {
        view.x += (event.clientX - pan.x) * (w / svg.getBoundingClientRect().width);
        view.y += (event.clientY - pan.y) * (h / svg.getBoundingClientRect().height);
        pan = { x: event.clientX, y: event.clientY };
        paintView();
        return;
      }
      var p = toWorld(event);
      if (dragging) { dragging.x = p.x; dragging.y = p.y; }
      else if (event.pointerType !== 'touch') magnet = p;
      wake();
    });
    svg.addEventListener('pointerleave', function () { magnet = null; wake(); });

    var pan = null;
    svg.addEventListener('pointerdown', function (event) {
      if (event.target.closest('.graph-node')) return;
      pan = { x: event.clientX, y: event.clientY };
      magnet = null;
      svg.setPointerCapture(event.pointerId);
      svg.classList.add('panning');
    });
    svg.addEventListener('pointerup', function () { pan = null; svg.classList.remove('panning'); });
    svg.addEventListener('wheel', function (event) {
      event.preventDefault();
      var rect = svg.getBoundingClientRect();
      var sx = (event.clientX - rect.left) * (w / rect.width);
      var sy = (event.clientY - rect.top) * (h / rect.height);
      var k = clamp(view.k * Math.exp(-event.deltaY * 0.0016), 0.5, 4);
      view.x = sx - (sx - view.x) * (k / view.k);
      view.y = sy - (sy - view.y) * (k / view.k);
      view.k = k;
      paintView();
    }, { passive: false });

    nodes.forEach(function (n) {
      var start = null;
      n.el.addEventListener('pointerdown', function (event) {
        dragging = n;
        start = { x: event.clientX, y: event.clientY };
        n.el.setPointerCapture(event.pointerId);
        wake();
      });
      n.el.addEventListener('pointerup', function () { if (dragging === n) { dragging = null; wake(); } });
      // A drag should move the node, not follow its link.
      n.el.addEventListener('click', function (event) {
        if (start && Math.abs(event.clientX - start.x) + Math.abs(event.clientY - start.y) > 5) event.preventDefault();
        start = null;
      });
      n.el.addEventListener('pointerenter', function () { focus(n, true); });
      n.el.addEventListener('pointerleave', function () { focus(n, false); });
    });

    container.appendChild(svg);
    // Settle most of the way before the first paint, so it does not explode into view.
    for (var s = 0; s < (reduced || big ? 320 : 120); s++) tick();
    wake();
  }

  function initGraph() {
    var data = window.GSOC_GRAPH;
    var box = document.getElementById('graph-container');
    if (!data || !box) return;
    var current = document.body.getAttribute('data-page');

    // The sidebar shows this page and what it links to. The full map is one click away.
    var near = {};
    near[current] = true;
    data.links.forEach(function (l) { if (l[0] === current) near[l[1]] = true; if (l[1] === current) near[l[0]] = true; });
    var local = {
      nodes: data.nodes.filter(function (n) { return near[n.id]; }),
      links: data.links.filter(function (l) { return near[l[0]] && near[l[1]]; })
    };
    if (local.nodes.length < 4) local = data;
    drawGraph(box, local, { current: current });
    box.appendChild(el('span', 'graph-hint', 'hover · drag · scroll to zoom'));

    var open = document.getElementById('graph-open');
    if (!open) return;
    var modal = null;
    open.addEventListener('click', function () {
      if (!modal) {
        modal = el('div', 'viewer graph-mode');
        modal.innerHTML = '<span class="viewer-title">Every page, and what links to what</span>' +
          '<div class="graph-container viewer-graph"></div>' +
          '<button type="button" class="icon-btn viewer-close" aria-label="Close">' + ICON.close + '</button>';
        document.body.appendChild(modal);
        var shut = function () { modal.classList.remove('open'); document.body.style.overflow = ''; open.focus(); };
        $('.viewer-close', modal).addEventListener('click', shut);
        modal.addEventListener('click', function (event) { if (event.target === modal) shut(); });
        document.addEventListener('keydown', function (event) { if (event.key === 'Escape' && modal.classList.contains('open')) shut(); });
      }
      modal.classList.add('open');
      document.body.style.overflow = 'hidden';
      drawGraph($('.viewer-graph', modal), data, { current: current, big: true });
    });
  }

  /* ---------- start ---------- */
  function start() {
    var toggle = document.getElementById('theme-toggle');
    if (toggle) toggle.addEventListener('click', function () { toggleTheme(toggle); });
    initFolds();
    initToc();
    initProgress();
    initReveal();
    initCode();
    initTips();
    initFilters();
    initViewer();
    initGraph();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
