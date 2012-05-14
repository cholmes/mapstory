Ext.onReady(function() {
    var start = 0,
    limit = 10,
    loadnotify = Ext.get('loading'),
    itemTemplate = "<li class='tile' id='item{iid}'><img class='thumb {thumbclass}' src='{thumb}'></img>" +
    "<div class='infoBox'><div class='itemTitle'><a href='{detail}'>{title}</a></div>" +
    "<div class='itemInfo'>{_display_type}, by <a href='{owner_detail}'>{owner}</a> on {last_modified}</div>" +
    "<div class='itemAbstract'>Abstract: {abstract}</div>"+
    "<div class='rating'>{rating} stars</div>"+
    "<div class='actions' id='{_type}-{id}'></div>"+
    "<div></li>",
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
                r.thumb = static_url + "theme/img/silk/map.png";
                r.thumbclass = "missing";
            } else {
                r.thumbclass = "";
            }
            var item = itemTemplate.append(list,r,true);
            new Ext.ToolTip({
                target: 'item' + r.iid,
                html: r['abstract']
            });
            item.select('.thumb').item(0).on('click',function(ev) {
                expandTile(this.parent());
            });
        });
    }
    
    function expandTile(tile) {
        var row, tiles, insertionPoint, newTile, col, cls, ident;
        Ext.select('#bigtile').fadeOut().remove();
        newTile = tile.dom.cloneNode(true);
        newTile.id = 'bigtile';
        tiles = tile.parent().select('li');
        col = tiles.indexOf(tile) % 3;
        row = Math.floor(tiles.indexOf(tile) / 3) + 1;
        insertionPoint = (row * 3) - 1;
        newTile = new Ext.Element(newTile).insertAfter(tiles.item(insertionPoint));
        cls = 'pointerthing';
        if (col == 0) {
            cls = cls + ' one';
        } else if (col == 2) {
            cls = cls + ' three';
        }
        Ext.DomHelper.append(newTile,{tag:'span',html:'&#9651;',cls:cls});
        if (favorites_links_url) {
            ident = newTile.query('.actions')[0].id;
            Ext.Ajax.request({
                url: favorites_links_url + "?ident=" + ident,
                method: 'GET',
                success: function(results) {
                    newTile.query('.actions')[0].innerHTML = results.responseText;
                    enablePostButton('.add-to-favorites',updateFavorites);
                    enablePostButton('.add-to-map',updateFavorites);
                }
            });
        }
        newTile.show().frame();
    }
    
    function updateFavorites(resp, opts) {
        Ext.Ajax.request({
            url: favorites_list_url,
            success: function(resp, opts) {
                Ext.get('favorites').dom.innerHTML = resp.responseText;
            }
        })
    }
    
    function enablePostButton(selector, callback) {
        Ext.select(selector).on('click',function(ev) {
            ev.preventDefault();
            Ext.Ajax.request({
                url: this.getAttribute('href'),
                method: 'POST',
                defaultHeaders : {
                    "X-CSRFToken" : Ext.util.Cookies.get('csrftoken')
                },
                success: callback
            })
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
            url: search_url,
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
    var scrollEl = Ext.isIE ? window : document;
    Ext.fly(scrollEl).on('scroll',function() {
        if (start < 0) return;
        var list = Ext.get('search_results').parent('.box'),
            scroll = Ext.fly(document).getScroll().top,
            view = 'innerHeight' in window ? window.innerHeight : document.documentElement.clientHeight,
            bottom = list.getBottom();
        if (scroll + view > bottom) {
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
    Ext.select('#sortForm select').on('change',function(ev) {
        queryItems['sort'] = this.value;
        reset();
    });

});
