/**
 * GA4 Event Tracking for Miami Yacht Collective
 * Tracks: modal_open, call_click, whatsapp_click
 */
(function () {
  'use strict';

  // Derive a readable page name from the URL
  function getPageName() {
    var path = window.location.pathname.replace(/\/$/, '');
    if (!path || path === '') return 'home';
    return path.split('/').pop().replace('.html', '');
  }

  var pageName = getPageName();

  // Track modal opens — any element with [data-modal]
  document.querySelectorAll('[data-modal]').forEach(function (el) {
    el.addEventListener('click', function () {
      if (typeof gtag === 'function') {
        gtag('event', 'modal_open', {
          page_name: pageName,
          transport_type: 'beacon'
        });
      }
    });
  });

  // Track call button clicks
  document.querySelectorAll('.modal-btn-call').forEach(function (el) {
    el.addEventListener('click', function () {
      if (typeof gtag === 'function') {
        gtag('event', 'call_click', {
          page_name: pageName,
          transport_type: 'beacon'
        });
      }
    });
  });

  // Track WhatsApp button clicks
  document.querySelectorAll('.modal-btn-wa').forEach(function (el) {
    el.addEventListener('click', function () {
      if (typeof gtag === 'function') {
        gtag('event', 'whatsapp_click', {
          page_name: pageName,
          transport_type: 'beacon'
        });
      }
    });
  });
})();
