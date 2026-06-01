/* ==========================================================================
   modern.js  —  Additive UI enhancements for the SMS (AdminLTE 3 / BS4)
   --------------------------------------------------------------------------
   Pure vanilla ES6, wrapped in an IIFE (no globals). Purely progressive
   enhancement: it attaches new, non-blocking behaviour and never modifies or
   removes the existing jQuery / AdminLTE handlers (ChartJS, select2,
   DataTables, formset, etc.). Safe to remove to fully revert.
   ========================================================================== */
(function () {
  'use strict';

  /* ---------------------------------------------------------------------- */
  /* 1. Smooth entrance for the main content area.                          */
  /* ---------------------------------------------------------------------- */
  function applyFadeIn() {
    var content = document.querySelector('.content-wrapper');
    if (content && !content.classList.contains('fade-in')) {
      content.classList.add('fade-in');
    }
  }

  /* ---------------------------------------------------------------------- */
  /* 2. Loading state on form submit.                                       */
  /*    Adds a spinner to the submit button so users get instant feedback.  */
  /*    - Runs only after the browser accepts the submit (native HTML5      */
  /*      validation still fires first and will cancel a submit event).     */
  /*    - Opt out per-form with `data-no-loading`.                          */
  /* ---------------------------------------------------------------------- */
  function wireFormLoadingStates() {
    var forms = document.querySelectorAll('form');
    Array.prototype.forEach.call(forms, function (form) {
      if (form.hasAttribute('data-no-loading')) {
        return;
      }
      form.addEventListener('submit', function () {
        // If the form is invalid, the submit event won't fire, so reaching
        // here means the submission is genuinely proceeding.
        var btn = form.querySelector(
          'button[type="submit"], input[type="submit"]'
        );
        if (!btn || btn.classList.contains('btn-loading')) {
          return;
        }
        // Defer one tick so the value is still sent with the request.
        window.setTimeout(function () {
          btn.classList.add('btn-loading');
          btn.setAttribute('aria-busy', 'true');
        }, 0);
      });
    });
  }

  /* ---------------------------------------------------------------------- */
  /* 3. Auto-dismiss success alerts (cosmetic).                             */
  /* ---------------------------------------------------------------------- */
  function autoDismissAlerts() {
    var alerts = document.querySelectorAll('.alert-success');
    Array.prototype.forEach.call(alerts, function (alert) {
      window.setTimeout(function () {
        alert.style.transition = 'opacity 400ms ease';
        alert.style.opacity = '0';
        window.setTimeout(function () {
          if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
          }
        }, 400);
      }, 4500);
    });
  }

  /* ---------------------------------------------------------------------- */
  /* 4. Lucide icons.                                                       */
  /*    Loads the Lucide CDN bundle and renders any [data-lucide] elements  */
  /*    we add in templates. FontAwesome icons are untouched.               */
  /* ---------------------------------------------------------------------- */
  function loadLucide() {
    if (!document.querySelector('[data-lucide]')) {
      return; // nothing to render; skip the network request
    }
    var script = document.createElement('script');
    script.src = 'https://unpkg.com/lucide@latest/dist/umd/lucide.min.js';
    script.defer = true;
    script.onload = function () {
      if (window.lucide && typeof window.lucide.createIcons === 'function') {
        window.lucide.createIcons();
      }
    };
    document.head.appendChild(script);
  }

  /* ---------------------------------------------------------------------- */
  /* Init                                                                   */
  /* ---------------------------------------------------------------------- */
  function init() {
    applyFadeIn();
    wireFormLoadingStates();
    autoDismissAlerts();
    loadLucide();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
