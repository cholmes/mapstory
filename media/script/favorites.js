$(function() {
    $(document).on('click',".rm-favorite",function(ev) {
        var el = $(this);
        ev.preventDefault();
        $.post(el.attr('href'),function() {
           el.closest('li').fadeOut(); 
        });
    });
    $(".add-to-favorites").click(function(ev) {
        var el = $(this);
        ev.preventDefault();
        $.post(el.attr('href'));
    });
    $(".add-to-map").click(function(ev) {
        var el = $(this);
        ev.preventDefault();
        $.post(el.attr('href'));
    });
});