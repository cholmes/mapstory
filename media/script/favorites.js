$(function() {
    $(".rm-favorite").click(function(ev) {
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
});