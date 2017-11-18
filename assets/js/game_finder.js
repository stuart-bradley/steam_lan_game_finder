/**
 * Created by wackm on 18-Nov-17.
 */
$(document).ready(function (e) {
    $("#form_submit").click(function () {
        if ($('#id_user_strings').val() != "") {
            var spinner_html = $('<i class="fa fa-spinner fa-pulse fa-2x fa-fw"></i> <span class="sr-only">Loading...</span>');
            var submit_button = $('#form_submit');
            submit_button.text('');
            submit_button.append(spinner_html);
        }
    });

    // Faking AJAX atm.
    $(".price-update").click(function (e) {
        var price_button = $(e.target);
        price_button.addClass('fa-spin')
        setTimeout(function () {
            price_button.removeClass('fa-spin')
        }, 2000);
    });
});