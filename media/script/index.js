$(function() {
    function adjustSizes() {
        var left = $(".span8 .box"),
        padding = left.outerHeight(true) - left.height(),
        target = $(".span4").height() - padding, 
        other = $("#sections").children().first().outerHeight(true);
        left.children().not("#sections").each(function(i,e) {
            other += $(e).outerHeight(true);
        });
        $("#sections .paginate-contents").height(target - other);
    }
    
    function noDataForTab(tabContent) {
        $(".noitems.tmpl").clone().css('display','').removeClass('tmpl').appendTo(tabContent.find('.paginate-contents'));
    }
    
    function loadTab(tabContent) {
        fetchMore(tabContent.find('.pagination .more'), function(els) {
            if (els.length == 0 && tabContent.find('article').length == 0) {
                noDataForTab(tabContent);
            }
        });
    }
    
    $("#sections [data-toggle=tab]").each(function() {
        var tab = $(this),
            tabContent = $("[id=" + $(this).attr('href').substring(1) + "]");
        if (tabContent.hasClass('active') && tabContent.find('article').length == 0) {
            loadTab(tabContent);
        }
        tab.on('shown', function() {
            if (tabContent.find('article').length == 0) {
                loadTab(tabContent)
            }
        });
    });

    (function adjustStoryTellers() {
        //+ Jonas Raoni Soares Silva
        //@ http://jsfromhell.com/array/shuffle [v1.0]
        function shuffle(o){ //v1.0
            for(var j, x, i = o.length; i; j = parseInt(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
            return o;
        };
        var height = 0, els = $(".storyteller");
        shuffle(els);
        els.appendTo(els.parent());
        els.slice(0,3).each(function(i, e) {
            height += $(e).outerHeight();
        });
        els.parent('.scroll-container').height(height);
    })();
    
    adjustSizes();
    
    
});