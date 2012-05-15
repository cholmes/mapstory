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
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    $(document).ajaxSend(function(event, xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken')); 
    });
});