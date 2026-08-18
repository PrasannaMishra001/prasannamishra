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

  if (headings.length) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var link = document.querySelector('.toc-content a[href="#' + entry.target.id + '"]');
        if (link) link.classList.toggle('in-view', entry.isIntersecting);
      });
    }, { rootMargin: '-10% 0px -70% 0px' });
    headings.forEach(function (h) { observer.observe(h); });
  }

  var graph = document.getElementById('graph-container');
  if (graph) drawGraph(graph);
});

function drawGraph(container) {
  var nodes = JSON.parse(container.dataset.nodes);
  var current = container.dataset.current;
  var w = 260, h = 250, cx = w / 2, cy = h / 2, r = 68;
  var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
  svg.setAttribute('width', '100%');
  svg.setAttribute('height', '100%');

  var placed = nodes.map(function (n, i) {
    var angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2;
    return { node: n, x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  });

  placed.forEach(function (a, i) {
    placed.slice(i + 1).forEach(function (b) {
      var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', a.x); line.setAttribute('y1', a.y);
      line.setAttribute('x2', b.x); line.setAttribute('y2', b.y);
      line.setAttribute('stroke', '#b8b8b8');
      line.setAttribute('stroke-width', '0.6');
      svg.appendChild(line);
    });
  });

  placed.forEach(function (p) {
    var active = p.node.href === current;
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
