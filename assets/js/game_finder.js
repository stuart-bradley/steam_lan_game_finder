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

    $(".price-update").click(function (e) {
        var price_button = $(e.target);
        var parent_td = $(price_button.parent().parent());
        var appid = $(parent_td.parent().children().first());
        $.ajax({
            url: '/ajax/update_price/',
            data: {
                'appid': appid.text()
            },
            dataType: 'json',
            beforeSend: function () {
                price_button.addClass('fa-spin');
            },
            success: function (result) {
                if (result['price']) {
                    var td_html = parent_td.html();
                    td_html = td_html.replace(/\$\d*\.\d*/g, result['price']);
                    td_html = td_html.replace(/Free/g, result['price']);
                    td_html = td_html.replace(/\d*-\d*-\d*/g, result['modified_date']);
                    parent_td.html(td_html);
                } else {
                    alert(result['error']);
                }
            },
            error: function (xhr, textStatus, error) {
                console.log(error);
            },
            complete: function () {
                price_button.removeClass('fa-spin');
            }
        });
    });
});