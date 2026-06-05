/*
 * Generic AJAX modal controller (Bootstrap 4.4.1 + jQuery + select2).
 *
 * Drives every `#addAss` trigger on the page:
 *   - Create Assignment  (dashboard / staff_dashboard)
 *   - Edit Submission    (submission_detail)
 *   - Grade Submission   (staff_assignment_submissions)
 *
 * The trigger only needs:  id="addAss"  href="<url that returns the form partial>"
 * Optionally  data-target="#someModalId"  (defaults to #genericModel).
 *
 * IMPORTANT: triggers must NOT carry `data-toggle="modal"`. This script owns the
 * open/close lifecycle; letting Bootstrap also auto-open the modal applies the
 * backdrop twice and freezes the page (the historic "double-open" bug). The script
 * additionally defends against a leftover backdrop on every hide.
 */
(function ($) {
    'use strict';

    // Guard against the file being included twice on one page.
    if (window.__ajaxModalInit) {
        return;
    }
    window.__ajaxModalInit = true;

    var DEFAULT_MODAL = '#genericModel';

    // ---- helpers -----------------------------------------------------------

    function resolveModal($trigger) {
        var target = $trigger.attr('data-target') || $trigger.data('target') || DEFAULT_MODAL;
        var $modal = $(target);
        if (!$modal.length) {
            console.warn('[ajax-modal] no modal found for target', target);
            return null;
        }
        return $modal;
    }

    // CRITICAL: the modal markup lives inside `.content-wrapper`, which (via the
    // modern.css redesign) can carry a `transform`/`filter`/`background-attachment:
    // fixed`. Any of those makes a `position: fixed` descendant resolve against that
    // ancestor instead of the viewport, so the modal backdrop covers the whole page
    // and swallows every click — the app appears frozen until reload. Moving the
    // modal to be a direct child of <body> escapes that containing block entirely.
    // Idempotent: once relocated, it stays put.
    function ensureModalAtBody($modal) {
        var el = $modal.get(0);
        if (el && el.parentNode !== document.body) {
            document.body.appendChild(el);
        }
        return $modal;
    }

    function loadingMarkup() {
        return (
            '<div class="text-center py-5 text-muted">' +
            '  <div class="spinner-border text-primary" role="status" aria-hidden="true"></div>' +
            '  <p class="mt-3 mb-0">Loading form&hellip;</p>' +
            '</div>'
        );
    }

    // Tear down any select2 widgets inside the modal before its HTML is replaced,
    // otherwise the orphaned widgets leak and can trap keyboard focus.
    function destroySelect2($scope) {
        if (!$.fn.select2) {
            return;
        }
        $scope.find('select.select2-hidden-accessible').each(function () {
            try {
                $(this).select2('destroy');
            } catch (e) {
                /* already destroyed - ignore */
            }
        });
    }

    // Initialise select2 for every <select> in the modal, scoped so the dropdown
    // lives inside the modal (keeps the modal focus-trap from blocking the search).
    function initSelect2($modal) {
        if (!$.fn.select2) {
            return;
        }
        $modal.find('select').each(function () {
            var $sel = $(this);
            if ($sel.hasClass('select2-hidden-accessible')) {
                return; // already initialised
            }
            $sel.select2({
                dropdownParent: $modal,
                width: '100%'
            });
        });
    }

    // Defensive cleanup: Bootstrap normally manages this, but a half-finished
    // open/close cycle can leave an orphan backdrop that freezes the page.
    function cleanupBackdrop() {
        if (!$('.modal.show').length) {
            $('.modal-backdrop').remove();
            $('body').removeClass('modal-open').css({
                'overflow': '',
                'padding-right': ''
            });
        }
    }

    // Detect Django form validation errors in a returned HTML fragment.
    function hasFormErrors(html) {
        var $r = $('<div>').html(html);
        return $r.find('.text-danger, .errorlist, .invalid-feedback, .is-invalid').length > 0;
    }

    // ---- open: fetch the form and show the modal ---------------------------

    $(document).on('click', '#addAss', function (e) {
        e.preventDefault();

        var $trigger = $(this);
        var url = $trigger.attr('href');
        if (!url || url === '#') {
            console.error('[ajax-modal] trigger #addAss has no usable href');
            return;
        }

        var $modal = resolveModal($trigger);
        if (!$modal) {
            return;
        }
        ensureModalAtBody($modal);

        var $body = $modal.find('.modal-body');

        destroySelect2($modal);
        $body.html(loadingMarkup());
        $modal.modal('show');

        $.ajax({
            url: url,
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function (response) {
                $body.html(response);
                initSelect2($modal);
                autofocusFirstField($modal);
            },
            error: function (xhr) {
                console.error('[ajax-modal] failed to load form', xhr);
                $body.html(
                    '<div class="alert alert-danger m-3">' +
                    'Failed to load the form. Please close and try again.<br>' +
                    '<small>Error: ' + xhr.status + ' ' + (xhr.statusText || '') + '</small>' +
                    '</div>'
                );
            }
        });
    });

    // Put keyboard focus on the first field the user should fill, skipping hidden,
    // disabled, csrf, and file inputs (focusing a file input is a dead end).
    function autofocusFirstField($modal) {
        var el = $modal
            .find('input, select, textarea')
            .filter(function () {
                var t = (this.type || '').toLowerCase();
                return t !== 'hidden' && t !== 'file' && this.name !== 'csrfmiddlewaretoken' &&
                    !this.disabled && !this.readOnly && $(this).is(':visible');
            })
            .first();
        if (el.length) {
            // select2 hides the real <select>; focus its rendered control instead.
            if (el.is('select') && el.hasClass('select2-hidden-accessible')) {
                return; // leave select2 alone; user can click it
            }
            el.trigger('focus');
        }
    }

    // Show the chosen filename under a file input (cosmetic feedback).
    function showFileName(input) {
        var $input = $(input);
        var $line = $input.next('.file-name');
        if (!$line.length) {
            $line = $('<small class="file-name"></small>');
            $input.after($line);
        }
        if (input.files && input.files.length) {
            var name = input.files.length > 1
                ? input.files.length + ' files selected'
                : input.files[0].name;
            $line.html('<i class="fas fa-paperclip"></i>' + $('<span>').text(name).html())
                 .addClass('has-file');
        } else {
            $line.removeClass('has-file').empty();
        }
    }

    $(document).on('change', '.modal input[type="file"]', function () {
        showFileName(this);
    });

    // Re-init select2 once the modal is fully shown (widths compute correctly
    // against the visible modal). Safe to call repeatedly - initSelect2 is idempotent.
    $(document).on('shown.bs.modal', '.modal', function () {
        var $modal = $(this);
        initSelect2($modal);
        autofocusFirstField($modal);
    });

    // Backdrop hygiene on every close.
    $(document).on('hidden.bs.modal', '.modal', function () {
        destroySelect2($(this));
        cleanupBackdrop();
    });

    // ---- submit: post the form via AJAX ------------------------------------

    $(document).on('submit', '.modal form', function (e) {
        e.preventDefault();

        var form = this;
        var $form = $(form);
        var $modal = $form.closest('.modal');
        var $submit = $form.find('button[type="submit"], input[type="submit"]');
        var originalHtml = $submit.first().html();

        $submit.prop('disabled', true).html(
            '<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Saving&hellip;'
        );

        $.ajax({
            url: $form.attr('action') || window.location.href,
            type: ($form.attr('method') || 'POST').toUpperCase(),
            data: new FormData(form),
            processData: false,
            contentType: false,
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function (response) {
                if (hasFormErrors(response)) {
                    // Re-render the form with its inline errors; keep the modal open.
                    destroySelect2($modal);
                    $modal.find('.modal-body').html(response);
                    initSelect2($modal);
                } else {
                    $modal.modal('hide');
                    window.location.reload();
                }
            },
            error: function (xhr) {
                console.error('[ajax-modal] submit failed', xhr);
                alert('Error: ' + (xhr.statusText || 'Something went wrong. Please try again.'));
            },
            complete: function () {
                $submit.prop('disabled', false).html(originalHtml);
            }
        });
    });
})(jQuery);
