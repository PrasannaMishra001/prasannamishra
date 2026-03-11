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
