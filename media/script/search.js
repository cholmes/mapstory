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
    "</li>",
    ownerTemplate = "<li class='tile' id='item{iid}'><img class='thumb {thumbclass}' src='{thumb}'></img>" +
    "<div class='infoBox'><div class='itemTitle'><a href='{detail}'>{title} {organization}</a></div>" +
    "<div class='itemInfo'>{_display_type}, joined on {last_modified}</div>" +
    "<div class='itemInfo'>{map_cnt} MapStories, {layer_cnt} StoryLayers</div>"+
    "<div class='itemAbstract'>{abstract}</div>"+
    "<div class='actions' id='{_type}-{id}'></div>"+
    "</li>" ,
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
    ownerTemplate = new Ext.DomHelper.createTemplate(ownerTemplate);
    ownerTemplate.compile();
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
            var item;
            if (r.thumb == null) {
                r.thumb = static_url + "theme/img/silk/map.png";
                r.thumbclass = "missing";
            } else {
                r.thumbclass = "";
            }
            if (r._type != 'owner') {
                item = itemTemplate.append(list,r,true);
            } else {
                r.thumbclass = "owner";
                item = ownerTemplate.append(list,r,true);
            }
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
    
    var searchWidget;
    SearchExtentControl = OpenLayers.Class(OpenLayers.Control, {
        type: OpenLayers.Control.TYPE_TOOL,
        layer: null,
        draw: function() {
            this.handler = new OpenLayers.Handler.Box( this, {
                "done": this.notice});
            this.handler.activate();
        },
        notice: function(bounds) {
            var proj = new OpenLayers.Projection('EPSG:4326'), box,
            ll = this.map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.left, bounds.bottom)),
            ur = this.map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.right, bounds.top));
            if (this.layer == null) {
                this.layer = new OpenLayers.Layer.Vector('boxes');
                this.map.addLayer(this.layer);
            }
            bounds = new OpenLayers.Bounds();
            bounds.extend(ll);
            bounds.extend(ur);
            box = new OpenLayers.Feature.Vector(bounds.toGeometry());
            this.layer.removeAllFeatures();
            this.layer.addFeatures(box);
            bounds = bounds.transform(this.map.getProjectionObject(),proj);
            searchByExtent(bounds);
        },
        CLASS_NAME: "SearchExtentControl"
    });
    SearchExtentTool = Ext.extend(gxp.plugins.Tool, {
        ptype: "search_extent",
        constructor: function(config) {
            SearchExtentTool.superclass.constructor.apply(this, arguments);
        },
        destroy: function() {
            SearchExtentTool.superclass.destroy.apply(this, arguments);
        },
        addActions: function() {
            var control = new SearchExtentControl();
            control.deactivate();
            var actions = [new GeoExt.Action({
                tooltip: "Tooltip",
                text: "Draw Area of Interest",
                iconCls: "gxp-icon-measure-area",
                enableToggle: true,
                pressed: false,
                allowDepress: true,
                control: control,
                map: this.target.mapPanel.map,
                toggleGroup: this.toggleGroup
            })];
            return SearchExtentTool.superclass.addActions.apply(this, [actions]);
        }
    });
    Ext.preg(SearchExtentTool.prototype.ptype, SearchExtentTool);
    function spatialSearch() {
        if (searchWidget == null) {
            var viewerConfig = {
                proxy: "/proxy/?url=",
                useCapabilities: false,
                useBackgroundCapabilities: false,
                useToolbar: false,
                useMapOverlay: false,
                portalConfig: {
                    border: false,
                    height: 512,
                    width: 512,
                    renderTo: "searchMap"
                },
                tools : [
                    {
                        ptype: "search_extent",
                        actionTarget: "map.tbar"
                    }
                ]
            }
            viewer_config.map.bbar = null;
            viewerConfig = Ext.apply(viewerConfig, viewer_config);

            searchWidget = new GeoExplorer.Viewer(viewerConfig);
        }
        $('#searchModal').modal();
    }
    function searchByExtent(bounds) {
        var key = "byextent", type="By Extent";
        queryItems[key] = bounds.toString();
        Ext.select('#refineSummary .' + type.replace(' ','_')).remove();
        addActiveFilter(type,key,'',bounds.toString(),false);
        reset();
        $('#searchModal').modal('hide');
    }
    
    function searchByPeriod(ev) {
        var keycode = (ev.keyCode ? ev.keyCode : ev.which);
        if (keycode == '13') {
            var key = "byperiod", type="By Period",
            start = Ext.get('time_start').getValue(),
            end =  Ext.get('time_end').getValue(),
            value = start + "," + end;
            queryItems[key] =  start + "," + end;
            Ext.select('#refineSummary .' + type.replace(' ','_')).remove();
            addActiveFilter(type,key,start + " to " + end,value,false);
            reset();
        }
    }

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
        if (h) {
            if (e.hasClass('refine')) {
                h.on('click',function() {
                    bbox.enable();
                });
            }
            h.on('click',function(ev) {
                toggleSection(Ext.get(this).parent());
            });
        }
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

    function addActiveFilter(typename,querykey,value,queryValue,multiple,callback) {
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
           if (typeof callback != 'undefined') {
               callback();
           }
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
    enableSearchLink('#byadded a','byadded',false);
    
    Ext.get('time_start').on('keypress',searchByPeriod);
    Ext.get('time_end').on('keypress',searchByPeriod);
    
    Ext.get('spatialSearch').on('click',spatialSearch);
    
    var authorStore = new Ext.data.JsonStore({
        url: author_api,
        root: 'names',
        totalProperty: 'totalCount',
        id: 'authorNames',
        idProperty: 'name',
        fields : [
            {name: 'name', mapping: 'name'}
        ]
    });

    function searchByAuthor(value) {
        queryItems['byowner'] = value;
        Ext.select('#refineSummary .By_StoryTeller').remove();
        addActiveFilter('By StoryTeller','byowner',value,value,false,function() {
            search.setValue('');
        });
        reset();
    }
    var search = new Ext.form.ComboBox({
        store        : authorStore,
        fieldLabel   : 'Author Name',
        displayField : 'name',
        typeAhead    : true,
        loadingText  : 'Searching...',
        minChars     : 3,
        width        : 175,
        renderTo     : 'who',
        onSelect     : function(record) {
            this.setValue(record.data.name);
            searchByAuthor(record.data.name);
            this.collapse();
        }
    });
    
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
