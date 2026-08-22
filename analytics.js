/* Offsetcheck — site-wide GA4 event wiring.
   Requires the inline gtag snippet (trackEvent) to be present. */
(function () {
  if (typeof window.trackEvent !== 'function') return;
  var page = location.pathname.split('/').pop() || 'index.html';

  // ---- Navigation clicks ----
  document.querySelectorAll('nav a[href]').forEach(function (a) {
    a.addEventListener('click', function () {
      trackEvent('nav_click', { link_text: a.textContent.trim().slice(0, 60), link_url: a.getAttribute('href'), page: page });
    });
  });

  // ---- Primary CTAs (explicitly labelled with data-cta) ----
  document.querySelectorAll('[data-cta]').forEach(function (el) {
    el.addEventListener('click', function () {
      trackEvent('cta_click', { cta: el.getAttribute('data-cta'), page: page });
    });
  });

  // ---- Outbound links ----
  document.querySelectorAll('a[href^="http"]').forEach(function (a) {
    if (a.hostname === location.hostname) return;
    a.addEventListener('click', function () {
      trackEvent('outbound_click', { domain: a.hostname, link_text: (a.textContent.trim() || a.href).slice(0, 90), page: page });
    });
  });

  // ---- Mailto links ----
  document.querySelectorAll('a[href^="mailto:"]').forEach(function (a) {
    a.addEventListener('click', function () {
      trackEvent('contact_email_clicked', { page: page });
    });
  });

  // ---- Theme toggle ----
  var tt = document.getElementById('themeToggle');
  if (tt) tt.addEventListener('click', function () {
    trackEvent('theme_toggled', { mode: document.documentElement.classList.contains('dark') ? 'dark' : 'light', page: page });
  });

  // ---- Scroll depth quartiles ----
  var marks = [25, 50, 75, 100], fired = {};
  addEventListener('scroll', function () {
    var h = document.documentElement;
    var pct = (h.scrollTop + innerHeight) / h.scrollHeight * 100;
    marks.forEach(function (m) {
      if (pct >= m && !fired[m]) { fired[m] = true; trackEvent('scroll_depth', { percent: m, page: page }); }
    });
  }, { passive: true });

  // ---- Section views ----
  if ('IntersectionObserver' in window) {
    var seen = {};
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && e.target.id && !seen[e.target.id]) {
          seen[e.target.id] = true;
          trackEvent('section_view', { section: e.target.id, page: page });
          so.unobserve(e.target);
        }
      });
    }, { threshold: 0.35 });
    document.querySelectorAll('section[id]').forEach(function (s) { so.observe(s); });
  }
})();
