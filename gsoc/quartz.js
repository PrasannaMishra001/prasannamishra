document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[data-fold]').forEach(function (button) {
    var target = document.getElementById(button.dataset.fold);
    button.addEventListener('click', function () {
      button.classList.toggle('collapsed');
      target.classList.toggle('collapsed');
    });
  });

  var links = Array.prototype.slice.call(document.querySelectorAll('.toc-content a'));
  var headings = links
    .map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); })
    .filter(Boolean);

  var explorerLinks = Array.prototype.slice.call(
    document.querySelectorAll('.explorer-content a[href^="#"]')
  );

  // The explorer lists sections rather than subsections, so a subsection keeps its
  // parent section highlighted.
  function explorerTarget(id) {
    var seen = null;
    for (var i = 0; i < headings.length; i++) {
      if (explorerHrefs['#' + headings[i].id]) seen = headings[i].id;
      if (headings[i].id === id) break;
    }
    return seen;
  }

  if (headings.length) {
    var explorerHrefs = {};
    explorerLinks.forEach(function (a) { explorerHrefs[a.getAttribute('href')] = true; });

    var visible = {};
    var current = null;
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var link = document.querySelector('.toc-content a[href="#' + entry.target.id + '"]');
        if (link) link.classList.toggle('in-view', entry.isIntersecting);
        visible[entry.target.id] = entry.isIntersecting;
      });
      for (var i = 0; i < headings.length; i++) {
        if (visible[headings[i].id]) { current = headings[i].id; break; }
      }
      var target = current === null ? null : explorerTarget(current);
      explorerLinks.forEach(function (a) {
        a.classList.toggle('active', a.getAttribute('href') === '#' + target);
      });
    }, { rootMargin: '-10% 0px -70% 0px' });
    headings.forEach(function (h) { observer.observe(h); });
  }

  var graph = document.getElementById('graph-container');
  if (graph) drawGraph(graph);
});

// The first node is the hub and every other node hangs off it, which is the shape
// of the work: one foundation with three things plugged into it.
function drawGraph(container) {
  var nodes = JSON.parse(container.dataset.nodes);
  var w = 260, h = 250, cx = w / 2, cy = h / 2 - 6, r = 74;
  var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
  svg.setAttribute('width', '100%');
  svg.setAttribute('height', '100%');

  var spokes = nodes.length - 1;
  var placed = nodes.map(function (n, i) {
    if (i === 0) return { node: n, x: cx, y: cy, hub: true };
    var angle = (2 * Math.PI * (i - 1)) / spokes - Math.PI / 2;
    return { node: n, x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  });

  placed.slice(1).forEach(function (b) {
    var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', placed[0].x); line.setAttribute('y1', placed[0].y);
    line.setAttribute('x2', b.x); line.setAttribute('y2', b.y);
    line.setAttribute('stroke', '#b8b8b8');
    line.setAttribute('stroke-width', '0.6');
    svg.appendChild(line);
  });

  placed.forEach(function (p) {
    var active = !!p.hub;
    var link = document.createElementNS('http://www.w3.org/2000/svg', 'a');
    link.setAttribute('href', p.node.href);

    var circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', p.x); circle.setAttribute('cy', p.y);
    circle.setAttribute('r', active ? 6 : 4);
    circle.setAttribute('fill', active ? '#284b63' : '#84a59d');
    link.appendChild(circle);

    var label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    label.setAttribute('x', p.x); label.setAttribute('y', p.y + 16);
    label.setAttribute('text-anchor', 'middle');
    label.setAttribute('class', 'node-label');
    label.textContent = p.node.label;
    link.appendChild(label);

    svg.appendChild(link);
  });

  container.appendChild(svg);
}
