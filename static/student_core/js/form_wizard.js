(function () {
  'use strict';

  function getFocusableFields(panel) {
    return Array.prototype.slice.call(
      panel.querySelectorAll('input:not([type="hidden"]), select, textarea')
    );
  }

  function validateStep(panel) {
    if (!panel) {
      return true;
    }

    var fields = getFocusableFields(panel);
    var firstInvalid = null;

    fields.forEach(function (field) {
      if (!field.checkValidity() && !firstInvalid) {
        firstInvalid = field;
      }
    });

    if (firstInvalid) {
      firstInvalid.reportValidity();
      firstInvalid.focus();
      return false;
    }

    return true;
  }

  function markCompleted(wizard, activeIndex) {
    var buttons = wizard.querySelectorAll('.form-wizard__step-button');

    Array.prototype.forEach.call(buttons, function (button, index) {
      button.classList.toggle('is-complete', index < activeIndex);
    });
  }

  function setStateClass(wizard, className, enabled) {
    var shell = wizard.querySelector('.form-wizard');

    wizard.classList.toggle(className, enabled);
    if (shell) {
      shell.classList.toggle(className, enabled);
    }
  }

  function updateActions(wizard, activeIndex, total) {
    var isFirst = activeIndex === 0;
    var isLast = activeIndex === total - 1;
    var previousButtons = wizard.querySelectorAll('.form-wizard__previous');
    var nextButtons = wizard.querySelectorAll('.form-wizard__next');
    var submitButtons = wizard.querySelectorAll('.form-wizard__submit');

    Array.prototype.forEach.call(previousButtons, function (button) {
      button.style.visibility = isFirst ? 'hidden' : '';
    });

    Array.prototype.forEach.call(nextButtons, function (button) {
      button.hidden = isLast;
      button.style.display = isLast ? 'none' : '';
    });

    Array.prototype.forEach.call(submitButtons, function (button) {
      button.hidden = !isLast;
      button.style.display = isLast ? 'inline-flex' : 'none';
    });
  }

  function showStep(wizard, index) {
    var panels = wizard.querySelectorAll('.form-wizard__panel');
    var buttons = wizard.querySelectorAll('.form-wizard__step-button');
    var total = panels.length;
    var nextIndex = Math.max(0, Math.min(index, total - 1));

    Array.prototype.forEach.call(panels, function (panel, panelIndex) {
      panel.classList.toggle('is-active', panelIndex === nextIndex);
      panel.hidden = panelIndex !== nextIndex;
    });

    Array.prototype.forEach.call(buttons, function (button, buttonIndex) {
      button.classList.toggle('is-active', buttonIndex === nextIndex);
      button.setAttribute('aria-selected', buttonIndex === nextIndex ? 'true' : 'false');
    });

    wizard.dataset.currentStep = String(nextIndex);
    setStateClass(wizard, 'is-first-step', nextIndex === 0);
    setStateClass(wizard, 'is-last-step', nextIndex === total - 1);
    markCompleted(wizard, nextIndex);
    updateActions(wizard, nextIndex, total);
  }

  function initWizard(wizard) {
    if (wizard.dataset.formWizardReady === 'true') {
      return;
    }

    wizard.dataset.formWizardReady = 'true';
    showStep(wizard, 0);

    wizard.addEventListener('click', function (event) {
      var currentIndex = Number(wizard.dataset.currentStep || 0);
      var activePanel = wizard.querySelector('.form-wizard__panel.is-active');
      var stepButton = event.target.closest('.form-wizard__step-button');
      var nextButton = event.target.closest('.form-wizard__next');
      var previousButton = event.target.closest('.form-wizard__previous');

      if (stepButton) {
        event.preventDefault();
        var targetIndex = Number(stepButton.dataset.stepIndex);
        if (targetIndex <= currentIndex || validateStep(activePanel)) {
          showStep(wizard, targetIndex);
        }
        return;
      }

      if (nextButton) {
        event.preventDefault();
        if (validateStep(activePanel)) {
          showStep(wizard, currentIndex + 1);
        }
        return;
      }

      if (previousButton) {
        event.preventDefault();
        showStep(wizard, currentIndex - 1);
      }
    });

    wizard.addEventListener('invalid', function (event) {
      var panels = wizard.querySelectorAll('.form-wizard__panel');

      Array.prototype.some.call(panels, function (panel, index) {
        if (panel.contains(event.target)) {
          showStep(wizard, index);
          return true;
        }
        return false;
      });
    }, true);
  }

  function init() {
    var wizards = document.querySelectorAll('[data-form-wizard]');
    Array.prototype.forEach.call(wizards, initWizard);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
