

const loader = $('<div>')
loader.attr('id', 'pre-loader')
loader.html('<div class="lds-facebook"><div></div><div></div><div></div></div>')

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
        },
        success: function(resp) {
            if (resp) {
                $('#uni_modal .modal-title').html($title)
                $('#uni_modal .modal-body').html(resp)
                if ($size != '') {
                    $('#uni_modal .modal-dialog').addClass($size + '  modal-dialog-centered')
                } else {
                    $('#uni_modal .modal-dialog').removeAttr("class").addClass("modal-dialog modal-md modal-dialog-centered")
                }
                $('#uni_modal').modal({
                    backdrop: 'static',
                    keyboard: false,
                    focus: true
                })
                $('#uni_modal').modal('show')
                end_loader()
            }
        }
    })
}
window._conf = function($msg = '', $func = '', $params = []) {
    $('#confirm_modal #confirm').attr('onclick', $func + "(" + $params.join(',') + ")")
    $('#confirm_modal .modal-body').html($msg)
    $('#confirm_modal').modal('show')
}

$(function() {
    $('#viewer_modal').on('shown.modal.bs', function() {
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
