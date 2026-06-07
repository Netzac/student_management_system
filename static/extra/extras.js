

const loader = $('<div>')
loader.attr('id', 'pre-loader')
loader.html('<div class="lds-facebook"><div></div><div></div><div></div></div>')

function ensure_modal_at_body(selector) {
    var $modal = $(selector)
    if ($modal.length && $modal[0].parentNode !== document.body) {
        document.body.appendChild($modal[0])
    }
    return $modal
}

function cleanup_modal_backdrops() {
    if ($('.modal.show').length === 0) {
        $('.modal-backdrop').remove()
        $('body').removeClass('modal-open').css({
            overflow: '',
            paddingRight: ''
        })
    }
}

window.start_loader = function() {
    $('body').removeClass('loading')
    if ($('#pre-loader').length > 0)
        $('#pre-loader').remove();
    $('body').append(loader)
    $('body').addClass('loading')
}
window.end_loader = function() {
    if ($('#pre-loader').length > 0)
        $('#pre-loader').remove();
    $('body').removeClass('loading')
}
window.uni_modal = function($title = '', $url = '', $size = "") {
    start_loader()
    $.ajax({
        url: $url,
        error: err => {
            console.log()
            alert("An error occured")
            end_loader()
            cleanup_modal_backdrops()
        },
        success: function(resp) {
            if (resp) {
                var $modal = ensure_modal_at_body('#uni_modal')
                $modal.find('.modal-title').html($title)
                $modal.find('.modal-body').html(resp)
                if ($size != '') {
                    $modal.find('.modal-dialog').removeAttr("class").addClass("modal-dialog " + $size + " modal-dialog-centered modal-dialog-scrollable")
                } else {
                    $modal.find('.modal-dialog').removeAttr("class").addClass("modal-dialog modal-md modal-dialog-centered modal-dialog-scrollable")
                }
                $modal.modal({
                    backdrop: 'static',
                    keyboard: false,
                    focus: true
                })
                $modal.modal('show')
                end_loader()
            } else {
                end_loader()
            }
        }
    })
}
window._conf = function($msg = '', $func = '', $params = []) {
    var $modal = ensure_modal_at_body('#confirm_modal')
    $modal.find('#confirm').attr('onclick', $func + "(" + $params.join(',') + ")")
    $modal.find('.modal-body').html($msg)
    $modal.modal('show')
}

$(function() {
    $('.modal').each(function() {
        ensure_modal_at_body('#' + this.id)
    })

    $(document).on('hidden.bs.modal', '.modal', cleanup_modal_backdrops)

    $('#viewer_modal').on('shown.bs.modal', function() {
        $('#zoom-value').val(100)
        $('#img-viewer img').css(
            'transform',
            'scale(1)'
        )

    })
    $('#zoom-plus').click(function() {
        var scale = parseFloat($('#zoom-value').val())
        if (scale >= 200) return false;
        scale += 10
        $('#zoom-value').val(scale)
        scale = scale / 100
        $('#img-viewer img').css(
            'transform',
            'scale(' + (scale) + ')'
        )
    })
    $('#zoom-minus').click(function() {
        var scale = parseFloat($('#zoom-value').val())
        if (scale <= 0) return false;
        scale -= 10
        $('#zoom-value').val(scale)
        scale = scale / 100
        $('#img-viewer img').css(
            'transform',
            'scale(' + (scale) + ')'
        )
    })

})
