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
        },function(resp) {
            $("#meta_data_status").hide();
            if (resp == 'OK') {
                $("#current_publish_status").html(link.html());
                link.closest('ul').find('.active').removeClass('active');
                link.closest('li').addClass('active');
            } else if (resp == 'META') {
                $("#meta_data_status").slideDown();
            } else {
                alert('Dang, unexpected response: ' + resp);
            }
        })
    });
    $("#show_additional_meta").click(function(ev) {
        $("#additional_meta").slideDown();
    });
    if (window.location.search.indexOf('describe') >= 0) {
        $(".tabbable a[href=#describemap]").tab('show');
    }
});