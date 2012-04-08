var quicksearch;
var menus;
function nixSearchLabel() {
    quicksearch.select('label').remove();
    quicksearch.select('input').focus();
    quicksearch.un('keypress',nixSearchLabel);
}
function enableMenu(rel) {
    menus.setVisible(false);
    var active;
    if (typeof(rel) == 'undefined') {
        active = Ext.select('#top-crossbar a.active_nav');
        if (active.getCount()) {
            rel = active.item(0).parent('li').getAttribute('rel');
        } else {
            rel = null;
        }
    }
    if (rel) {
        menus.item(0).parent('ul').select('[rel=' + rel + ']').show();
    }
}
function menu(rel) {
    Ext.select('#top-crossbar li[rel=' + rel + ']').on('mouseover',function() {
        enableMenu(rel);
    });
}
//@todo make login pages not produce error
if ('Ext' in window) {
    Ext.onReady(function() {
        quicksearch = Ext.get('quicksearch');
        quicksearch.on('keypress',nixSearchLabel);
        quicksearch.on('click',nixSearchLabel);
        menus = Ext.select('#sitenav li a').setVisibilityMode(Ext.Element.DISPLAY).setVisible(false,false);
        menu('category');
        menu('search');
        enableMenu();
        Ext.select('.noi').on('click',function(ev) {
            alert('Coming Soon...');
            ev.stopEvent();
        });
    });
}

$(function () {
    $('#login-link').click(function(e) {
        e.preventDefault();
        var href = $(this).attr('href');
        if (href[0] == '/') {
            $.post(href,{},function(d,s,x) {
                window.location.reload();
            })
        } else {
            $(href).toggle();
        }
    });
    $("#login-form-pop button").click(function(e) {
        var form = $("#login-form-pop form");
        e.preventDefault();
        $.post(form.attr('action'),form.serialize(),function(data,status,xhr) {
            if (status == 'success') {
                window.location.reload();
            } else {
                alert(data);
            }
            $("#login-form-pop").toggle();
        });
    })
});