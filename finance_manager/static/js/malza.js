$(function () {
    var new_row_button = $("#NewRow");
    var dynamic_form = $("form.dynamicForm");
    var dynamic_form_separator = $("#separator");
    var dynamic_form_counter = $('#id_form-TOTAL_FORMS');
    new_row_button.on("click", function () {
        var fieldSetToClone = dynamic_form.children("div")[0].outerHTML;
        console.log(fieldSetToClone);
        var ActualCounter = dynamic_form_counter.attr('value');
        fieldSetToClone = fieldSetToClone.replace(/-(\d)-/gm,`-${ActualCounter}-`);
        dynamic_form_counter.attr('value', parseInt(ActualCounter)+1);
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
});