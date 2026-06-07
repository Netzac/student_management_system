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
  /* 3. Dynamics 365 form accessibility and feedback enhancements.          */
  /*    Adds missing ARIA hooks, required markers, inline client-side        */
  /*    invalid feedback, and the requested empty-submit shake. It does not  */
  /*    alter Django validation, field names, actions, or submit behaviour.  */
  /* ---------------------------------------------------------------------- */
  function getFieldLabel(field) {
    if (field.id) {
      var explicit = null;
      var labels = document.querySelectorAll('label[for]');
      Array.prototype.some.call(labels, function (label) {
        if (label.getAttribute('for') === field.id) {
          explicit = label;
          return true;
        }
        return false;
      });
      if (explicit) {
        return explicit;
      }
    }

    var group = field.closest('.form-group, .input-group, .form-check, .custom-control');
    return group ? group.querySelector('label') : null;
  }

  function getFieldName(field) {
    var label = getFieldLabel(field);
    if (label) {
      return label.textContent.replace('*', '').trim();
    }
    return field.getAttribute('placeholder') || field.getAttribute('name') || 'This field';
  }

  function ensureFieldId(field, index) {
    if (!field.id) {
      field.id = 'm-field-' + index + '-' + Math.random().toString(36).slice(2, 7);
    }
  }

  function ensureRequiredMarker(field) {
    if (!field.required) {
      return;
    }

    var label = getFieldLabel(field);
    if (!label || label.querySelector('.m-required-mark')) {
      return;
    }

    var marker = document.createElement('span');
    marker.className = 'm-required-mark';
    marker.setAttribute('aria-hidden', 'true');
    marker.textContent = '*';
    label.appendChild(marker);
  }

  function ensureDescribedBy(field, describedById) {
    var current = field.getAttribute('aria-describedby');
    var ids = current ? current.split(/\s+/) : [];
    if (ids.indexOf(describedById) === -1) {
      ids.push(describedById);
      field.setAttribute('aria-describedby', ids.join(' ').trim());
    }
  }

  function ensureInlineError(field) {
    var group = field.closest('.form-group, .input-group, .form-check, .custom-control') || field.parentNode;
    if (!group) {
      return null;
    }

    var existing = group.querySelector('.invalid-feedback, .m-field-error');
    if (existing) {
      if (!existing.id) {
        existing.id = field.id + '-error';
      }
      ensureDescribedBy(field, existing.id);
      return existing;
    }

    var error = document.createElement('div');
    error.className = 'm-field-error';
    error.id = field.id + '-error';
    error.setAttribute('role', 'alert');
    error.hidden = true;
    group.appendChild(error);
    ensureDescribedBy(field, error.id);
    return error;
  }

  function setFieldInvalid(field, invalid) {
    var error = ensureInlineError(field);
    field.classList.toggle('m-invalid', invalid);
    field.setAttribute('aria-invalid', invalid ? 'true' : 'false');

    if (!error) {
      return;
    }

    if (invalid) {
      var message = field.validationMessage || getFieldName(field) + ' is required.';
      error.textContent = '\u26a0 ' + message;
      error.hidden = false;
    } else if (error.classList.contains('m-field-error')) {
      error.textContent = '';
      error.hidden = true;
    }
  }

  function shakeForm(form) {
    form.classList.remove('m-form-shake');
    // Restart animation reliably.
    void form.offsetWidth;
    form.classList.add('m-form-shake');
  }

  function enhanceForms() {
    var fields = document.querySelectorAll(
      'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]), select, textarea'
    );

    Array.prototype.forEach.call(fields, function (field, index) {
      ensureFieldId(field, index);

      var label = getFieldLabel(field);
      if (label && !label.getAttribute('for')) {
        label.setAttribute('for', field.id);
      }

      if (!field.getAttribute('aria-label') && !field.getAttribute('aria-labelledby') && !label) {
        field.setAttribute('aria-label', getFieldName(field));
      }

      ensureRequiredMarker(field);
      ensureInlineError(field);

      field.addEventListener('input', function () {
        if (field.classList.contains('m-invalid')) {
          setFieldInvalid(field, !field.checkValidity());
        }
      });

      field.addEventListener('blur', function () {
        if (field.required) {
          setFieldInvalid(field, !field.checkValidity());
        }
      });
    });

    var forms = document.querySelectorAll('form');
    Array.prototype.forEach.call(forms, function (form) {
      form.addEventListener('invalid', function (event) {
        setFieldInvalid(event.target, true);
        shakeForm(form);
      }, true);

      form.addEventListener('submit', function (event) {
        var invalidFields = form.querySelectorAll(
          'input:invalid, select:invalid, textarea:invalid'
        );

        if (!invalidFields.length) {
          return;
        }

        Array.prototype.forEach.call(invalidFields, function (field) {
          setFieldInvalid(field, true);
        });

        shakeForm(form);

        if (!form.hasAttribute('novalidate')) {
          event.preventDefault();
          invalidFields[0].focus();
        }
      }, true);
    });
  }

  /* ---------------------------------------------------------------------- */
  /* 4. Auto-dismiss success alerts (cosmetic).                             */
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
  /* 5. Lucide icons.                                                       */
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
  /* 6. Toast notifications (redesign.md micro-interaction).                 */
  /*    Exposes window.SMSModern.toast(message, type). Self-contained; uses  */
  /*    only the .m-toast* styles from modern.css.                          */
  /* ---------------------------------------------------------------------- */
  function getToastContainer() {
    var c = document.querySelector('.m-toast-container');
    if (!c) {
      c = document.createElement('div');
      c.className = 'm-toast-container';
      document.body.appendChild(c);
    }
    return c;
  }

  function toast(message, type) {
    var el = document.createElement('div');
    el.className = 'm-toast m-toast-' + (type || 'info');
    el.setAttribute('role', 'status');
    el.textContent = message;
    getToastContainer().appendChild(el);
    window.setTimeout(function () {
      el.classList.add('m-toast-hide');
      window.setTimeout(function () {
        if (el.parentNode) {
          el.parentNode.removeChild(el);
        }
      }, 260);
    }, 4000);
  }

  /* ---------------------------------------------------------------------- */
  /* Init                                                                   */
  /* ---------------------------------------------------------------------- */
  function init() {
    applyFadeIn();
    wireFormLoadingStates();
    enhanceForms();
    autoDismissAlerts();
    loadLucide();
    // Public, namespaced API (no bare globals).
    window.SMSModern = { toast: toast };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
