$(function () {
    var new_row_button = $("#NewRow");
    var dynamic_form = $("form.dynamicForm");
    var dynamic_form_separator = $("#separator");
    var dynamic_form_counter = $('#id_form-TOTAL_FORMS');
    new_row_button.on("click", function () {
        var fieldSetToClone = dynamic_form.children("div")[0].outerHTML;
        console.log(fieldSetToClone);
        var ActualCounter = dynamic_form_counter.attr('value');
        fieldSetToClone = fieldSetToClone.replace(/-(\d)-/gm, `-${ActualCounter}-`);
        dynamic_form_counter.attr('value', parseInt(ActualCounter) + 1);
        dynamic_form_separator.before(fieldSetToClone);
    });
    var expand = $(".expand");
    expand.each(function (index, element) {
        $(element).on("click", function () {
            var button = $(this);
            var details = button.parent().next();
            details.toggleClass("collapse");
        })
    });

    var date_field = $("input[name='date']");
    var date_field_class = $("input.date_field");

    jQuery.fn.forceNumeric = function () {
        return this.each(function () {
            $(this).keydown(function (e) {
                var key = e.which || e.keyCode;

                if (!e.shiftKey && !e.altKey && !e.ctrlKey &&
                    // numbers
                    key >= 48 && key <= 57 ||
                    key >= 96 && key <= 105 ||
                    key == 189 || key == 173 ||
                    key == 8 || key == 9 ||
                    key == 37 || key == 39 ||
                    key == 46)
                    return true;

                return false;
            });
        });
    };

});