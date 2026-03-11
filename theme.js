// Theme toggle with localStorage persistence
(function () {
  const toggle = document.getElementById('themeToggle');
  const html = document.documentElement;
  const STORAGE_KEY = 'portfolio-theme';

  // Load saved preference, default to light
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved === 'dark') {
    html.setAttribute('data-theme', 'dark');
  }

  toggle.addEventListener('click', function () {
    const isDark = html.getAttribute('data-theme') === 'dark';
    if (isDark) {
      html.removeAttribute('data-theme');
      localStorage.setItem(STORAGE_KEY, 'light');
    } else {
      html.setAttribute('data-theme', 'dark');
      localStorage.setItem(STORAGE_KEY, 'dark');
    }
  });
})();

// Navbar: scroll shadow, active section, hamburger
(function () {
  const nav = document.getElementById('glassNav');
  const hamburger = document.getElementById('navHamburger');
  const navLinks = nav.querySelector('.nav-links');
  const links = nav.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('.section');

  // Scroll shadow
  window.addEventListener('scroll', function () {
    nav.classList.toggle('scrolled', window.scrollY > 10);
  });

  // Active section highlighting
  function updateActive() {
    var scrollY = window.scrollY + 100;
    sections.forEach(function (sec) {
      var top = sec.offsetTop;
      var bottom = top + sec.offsetHeight;
      var id = sec.getAttribute('id');
      var link = nav.querySelector('.nav-link[href="#' + id + '"]');
      if (link) {
        link.classList.toggle('active', scrollY >= top && scrollY < bottom);
      }
    });
  }
  window.addEventListener('scroll', updateActive);
  updateActive();

  // Hamburger toggle
  hamburger.addEventListener('click', function () {
    hamburger.classList.toggle('open');
    navLinks.classList.toggle('open');
  });

  // Close menu on link click (mobile)
  links.forEach(function (link) {
    link.addEventListener('click', function () {
      hamburger.classList.remove('open');
      navLinks.classList.remove('open');
    });
  });
})();
