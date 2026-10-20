/* cli.sgit.ai — nav interaction, the same component sgit.ai runs.
   Two jobs, and only one of them needs JavaScript on desktop: hover and :focus-within
   open a dropdown in CSS alone. This handles the rest — the phone menu button, and the
   fact that a finger has no hover. If this file never loads the nav still works: every
   group label is a link to that section's own page. */
(function () {
  'use strict';
  /* The version badge and the footer's version link are filled here from assets/version.js
     (window.SITE_VERSION), the one place a release stamps it. Without JavaScript the badge is
     empty (and hidden by CSS) and the footer link reads "release history" — nothing is wrong,
     nothing is stale. Before v0.1.66 the version was stamped into every page, and a one-line
     release rewrote ~200 files. */
  function fillVersion(v) {
    var els = document.querySelectorAll('[data-site-version]');
    for (var i = 0; i < els.length; i++) els[i].textContent = v;
  }
  if (window.SITE_VERSION) {
    fillVersion(window.SITE_VERSION);
    /* version.js is served with a ten-minute cache, so a browser that had it before a release
       shows the old badge next to a freshly fetched page (seen on 6 Sep: the release row said
       v0.1.73, the badge v0.1.72). Refetch past the cache and refill if it moved. Best-effort:
       any failure leaves the cached value, which is never blank. */
    try {
      var tag = document.querySelector('script[src$="assets/version.js"]');
      if (tag && window.fetch) fetch(tag.getAttribute('src'), { cache: 'reload' }).then(function (r) { return r.ok ? r.text() : ''; }).then(function (s) {
        var m = /"(v\d+\.\d+\.\d+)"/.exec(s || '');
        if (m && m[1] !== window.SITE_VERSION) { window.SITE_VERSION = m[1]; fillVersion(m[1]); }
      }).catch(function () {});
    } catch (e) {}
  }
  var nav = document.querySelector('nav.site');
  if (!nav) return;
  var toggle = nav.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  /* On a touch screen the dropdown has no hover to open it: the first tap on a group
     label opens the menu, a second follows the link. Only where a dropdown is actually
     drawn — in the collapsed phone menu the children are already visible. */
  document.addEventListener('click', function (e) {
    var link = e.target.closest && e.target.closest('nav.site .ni-has > .nl');
    var open = nav.querySelector('.ni-has.open');
    if (open && (!link || link.parentNode !== open)) open.classList.remove('open');
    if (!link || !window.matchMedia || !window.matchMedia('(hover: none)').matches) return;
    var item = link.parentNode, sub = item.querySelector('.sub');
    if (sub && window.getComputedStyle(sub).position === 'absolute'
            && !item.classList.contains('open')) {
      e.preventDefault();
      item.classList.add('open');
    }
  });
  /* Escape closes whatever is open — keyboard users get out the same way everywhere. */
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = nav.querySelector('.ni-has.open');
    if (open) open.classList.remove('open');
    if (nav.classList.contains('open')) {
      nav.classList.remove('open');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    }
  });
}());
