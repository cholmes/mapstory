$(function() {
    $(".comments_tree").on("hover",".comment",function() {
        var el = $(this);
        el.toggleClass('palebg');
        el.find('.actions').toggle();
    }).on("click","a.d",function() {
        var el = $(this);
        $.post(el.attr('href'),function() {
            var comment = el.closest('li');
            if (comment.find('.comments_children').length) {
                comment.find('.comment_content').first().css('text-decoration','line-through');
            } else {
                comment.fadeOut();
            }
        });
        return false;
    }).on("click","a.r",function() {
        var el = $(this);
        $.get(el.attr('href'),function(data) {
            $("#comment_modal .modal-body").html(data).parent().modal('show').find('textarea').focus();
        })
        return false;
    }).on("click","a.f",function() {
        var el = $(this);
        $.get(el.attr('href'),function(data) {
            $("#comment_modal .modal-body").html(data).parent().modal('show').find('textarea').focus();
            $(".modal-body input[name=next]").val(window.location);
        })
        return false;
    });
    $("#comment_modal").modal({show:false});
});