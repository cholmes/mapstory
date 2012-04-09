Ext.onReady(function() {
    var start = 0,
    limit = 10,
    loadnotify = Ext.get('loading'),
    itemTemplate = "<li id='item{iid}'><a href='{detail}'><img class='thumb {thumbclass}' src='{thumb}'></img></a>" +
    "<div class='itemTitle'><a href='{detail}'>{title}</a></div>" +
    "<div class='itemInfo'>{_display_type}, by <a href='{owner_detail}'>{owner}</a> on {last_modified:date(\"F j, Y\")}</div>" +
    "<div class='itemAbstract>{abstract}</div>"+
    "<div class='rating'>{rating} stars</div>"+
    "</li>",
    filterTemplate = "<div class='removeFilter {typeclass}'><img height='8' src='/static/theme/img/silk/delete.png' class='removeFilter' href='#removeFilter'> </a><strong>{type}</strong> {value}</div>",
    fetching = false,
    list = Ext.get(Ext.query('#search_results ul')[0]),
    store = new Ext.data.JsonStore({
        autoDestroy: true,
        storeId: 'items',
        root: 'rows',
        idProperty: 'iid',
        fields: ['title','name'],
        listeners: []
    }),
    selModel = null,
    dataCartStore = null,
    queryItems = {},
    totalQueryCount;

    itemTemplate = new Ext.DomHelper.createTemplate(itemTemplate);
    itemTemplate.compile();
    filterTemplate = new Ext.DomHelper.createTemplate(filterTemplate);
    filterTemplate.compile();

    function handleSave(item) {
        window.open(item.link);
    }

    function handleSelect(button) {
        var selected = button.iconCls == 'cartAddButton';
        var clazz = selected ? 'cartRemoveButton' : 'cartAddButton';
        button.setIconClass(clazz);
        selModel.select(this.iid,selected);
    }

    function handleAddToMap(item) {
        alert("You want to add " + item.title + " to a new map. I'm afraid this is not implemented.");
    }

    function updateDisplaying() {
        var cnt = store.getCount(), 
            displaying = Ext.get('displaying'),
            note = Ext.get('displayNote');
        if (cnt == 0) {
            displaying.hide();
            note.hide();
        } else {
            if (cnt == totalQueryCount) {
                note.hide();
            } else {
                note.show();
            }
            displaying.dom.innerHTML = "Displaying " + cnt + " of " + totalQueryCount;
            displaying.show();
        }
    }

    function appendResults(results) {
        fetching = false;
        loadnotify.hide();
        results = Ext.util.JSON.decode(results.responseText);
        totalQueryCount = results.total;
        var read = store.reader.readRecords(results);
        if (read.records.length == 0) {
            if (start == 0) {
                Ext.DomHelper.append(list,'<li class="noresults"><h4 class="center">No Results</h4></li>');
            }
            start = -1;
            updateDisplaying();
            return;
        } else {
            start += limit;
        }
        store.add(read.records);
        updateDisplaying();
        var saveListeners = {
            click: handleSave
        };
        Ext.each(results.rows,function(r,i) {
            if (r.thumb == null) {
                r.thumb = "{{ STATIC_URL }}theme/img/silk/map.png";
                r.thumbclass = "missing";
            } else {
                r.thumbclass = "";
            }
            var item = itemTemplate.append(list,r,true);
            new Ext.ToolTip({
                target: 'item' + r.iid,
                html: r['abstract']
            });
        });

    }

    function reset() {
        store.removeAll(false);
        list.select('li').remove();
        start = 0;
        fetch();
    }

    function fetch() {
        if (fetching) return;
        if (start < 0) return;
        loadnotify.show();
        fetching = true;
        var params = Ext.apply({
                start: start,
                limit: limit
            },queryItems);
        Ext.Ajax.request({
            url: '{% url new_search_api %}',
            method: 'GET',
            success: appendResults,
            params: params
        });
    }

    if (init_search) {
        if (init_search.q) {
            Ext.get('searchField').dom.value = init_search.q;
        }
        if ('bytype' in init_search) {
            Ext.get('bytype').parent('.refineSection').setVisibilityMode(Ext.Element.DISPLAY).hide();
        }
        queryItems = init_search;
    }
    fetch();
    var scrollEl = Ext.isIE ? document.body : document;
    Ext.fly(scrollEl).on('scroll',function() {
        if (start < 0) return;
        var list = Ext.get('search_results');
        var scroll = Ext.fly(document).getScroll().top;
        var height = list.getHeight() + list.getTop();
        var windowHeight = Ext.isIE ? document.body.clientHeight : window.innerHeight;
        if (scroll + windowHeight > height) {
            fetch();
        }
    });

    function toggleSection(el) {
        var expand = el.hasClass('collapsed');
        var isbbox = el.dom.id == 'refine';
        if (expand) {
            if (isbbox) {
                bbox.enable();
            }
            expandSection(el);
        } else {
            collapseSection(el);
            if (isbbox) {
                bbox.disable();
            }
        }
        el.toggleClass('collapsed');
        el.toggleClass('expand');
    }
    function expandSection(el) {
        el.select('.refineControls').slideIn('t',{useDisplay:true});
    }
    function collapseSection(el) {
        el.select('.refineControls').slideOut('t',{useDisplay:true});
    }
    Ext.select('.refineSection').each(function(e,i) {
        if (e.hasClass('collapsed')) {
            collapseSection(e);
        }
        var h = e.first('h5');
        if (e.hasClass('refine')) {
            h.on('click',function() {
                bbox.enable();
            });
        }
        h.on('click',function(ev) {
            toggleSection(Ext.get(this).parent());
        });
    });

    // fake the grid selection model
    var SelectionModel = new Ext.extend(Ext.util.Observable, {
        grid : {
            store: store
        },
        constructor : function(config) {
            Ext.apply(this, config);
            this.addEvents('rowselect','rowdeselect')
        },
        getButton : function(el) {
            // maybe a better way to do this?
            return Ext.getCmp(el.parent('.x-btn').id);
        },
        clearSelections : function() {
            Ext.select('.cartRemoveButton').each(function(e,i) {
                this.getButton(e).setIconClass('cartAddButton');
            }, this);
        },
        selectRow : function(index, keepExisting) {
            this.getButton(Ext.get('toggle' + index)).setIconClass('cartRemoveButton');
        },
        select: function(index,selected) {
            var record = store.getAt(index);
            this.fireEvent(selected ? 'rowselect' : 'rowdeselect',this,index,record);
        }
    });
    
    function updateAciveFilterHeader() {
        if (Ext.get("refineSummary").select('div').getCount()) {
            Ext.select("#refineSummary h5").show();
        } else {
            Ext.select("#refineSummary h5").setVisibilityMode(Ext.Element.DISPLAY).hide();
        }
    }

    function addActiveFilter(typename,querykey,value,queryValue,multiple) {
        var el = filterTemplate.append("refineSummary",{typeclass:typename.replace(' ','_'),type:typename,value:value},true);
        el.on('click',function(ev) {
           ev.preventDefault();
           el.remove();
           if (multiple) {
               queryItems[querykey].remove(queryValue);
               if (queryItems[querykey].length == 0) {
                   delete queryItems[querykey];
               }
           } else {
               delete queryItems[querykey];
           }
           reset();
           updateAciveFilterHeader();
        });
        updateAciveFilterHeader();
    }

    function enableSearchLink(selector,querykey,multiple) {
        Ext.select(selector).on('click',function(ev) {
            ev.preventDefault();
            var anchor = Ext.get(this),
                href =  anchor.getAttribute('href'),
                filterType,
                existing;
            if (href[0] == '#') {
                href = href.substring(1);
            } else {
                // IE...
                href = href.substring(href.indexOf("#") + 1);
            }
            if (multiple) {
                existing = queryItems[querykey] || [];
                existing.push(href);
                queryItems[querykey] = existing;
            } else {
                queryItems[querykey] = href;
            }
            filterType = anchor.parent('.refineSection').first('h5').dom.innerHTML;
            if (!multiple) {
                Ext.select('#refineSummary .' + filterType.replace(' ','_')).remove();
            }
            addActiveFilter(filterType, querykey, anchor.dom.innerHTML, href, multiple);
            reset();
        });
    }
    enableSearchLink('#bytype a','bytype',false);
    enableSearchLink('#bykeyword a','bykw',false);
    enableSearchLink('#bysection a','bysection',false);
    
    new Ext.ToolTip({
        target: 'filter-tip'
    });
    
    // and combine with search form
    Ext.get('searchForm').on('keypress',function(ev) {
        var keycode = (ev.keyCode ? ev.keyCode : ev.which);
        if (keycode == '13') {
            ev.preventDefault();
            queryItems['q'] = this.dom.search.value;
            reset();
        }
    });
    Ext.get('sortForm').on('click',function(ev) {
        queryItems['sort'] = this.dom.sortby.value;
        reset();
    });

});
