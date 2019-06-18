$(function () {
    var button = $("#NewRow");
    var form = $(".dynamicForm form");
    button.on("click", function () {
        var fieldSetToClone = button.closest("fieldset");
        form.append(fieldSetToClone.innerHTML)
    })
});