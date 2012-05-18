$(function() {
    $("#submit").click(function(ev) {
        ev.preventDefault();
        var form = $(this).closest('form');
        form.find('.errorlist').fadeOut();
        $.post(
            form.attr('action'),
            form.serialize(),
            function() {
                alert('Updated');
            }
        ).error(function(ev) {
            $(ev.responseText).appendTo(form);
        });
    });
    $("#publish_status").click(function(ev) {
        ev.preventDefault();
        $.post(
            $(this).attr('href'),
            function() {
                $("#publish_info").fadeOut();
            }
        )
    });
    $("#topic-dropdown a").click(function(ev) {
        ev.preventDefault();
        $.post( topic_url, {
            'topics' : $(this).attr('href').substring(1)
        },function() {
            $(".topic-info.alert").fadeOut();  
        })
    });
    $("#publish-dropdown a").click(function(ev) {
        var link = $(this);
        ev.preventDefault();
        $.post( publishing_url, {
            'status' : link.attr('href').substring(1)
        },function() {
            $("#current_publish_status").html(link.html());
            link.closest('ul').find('.active').removeClass('active');
            link.closest('li').addClass('active');
        })
    });
});