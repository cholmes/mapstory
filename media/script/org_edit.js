$(function() {
    var panel = $("#editpanel"),
        widget = $("#editpanel-content"),
        msg = $("#editmsg"),
        currentWidget = null,
        currentAction = null,
        currentContent = null,
        handlers = {
            banner_image : {
                data : function(data) {
                    data[currentAction] = currentWidget.find('input').val();
                },
                success : function(resp) {
                    currentContent.find('img').show().attr('src',resp);
                }
            },
            org_content : {
                data: function(data) {
                    data[currentAction] = currentWidget.find('textarea').val();
                },
                success: function(resp) {
                    currentContent.html(resp);
                }
            }
        };

    function startEdit(el) {
        var action = el.attr('data-content'),
            parent = el.parent('.box'),
            position = parent.position();
        currentContent = el;
        widget.children('div').hide();
        currentWidget = $("#edit_" + action).show();
        panel.css({
            top: position.top,
            left: position.left,
            width: parent.outerWidth(),
            height: parent.outerHeight()
        });
        panel.show();
        currentAction = action;
    }
    
    function submit() {
        var handler = handlers[currentAction], data={};
        msg.html("Submitting");
        handler.data(data);
        $.post(window.location.pathname + "/api",data,function(resp) {
            currentContent.find('.placeholder').hide();
            handler.success(resp);
            panel.hide();
            msg.html('');
        });
    }
    
    widget.children('div').hide();
    $("a[href=#cancel]").click(function(ev) {
        ev.preventDefault();
        panel.hide();
    });
    $("a[href=#ok]").click(function(ev) {
        ev.preventDefault();
        submit();
    });
    $(".edit-btn").click(function(ev) {
        ev.preventDefault();
        startEdit($(this).parent().find('[data-content]'));
    });
});