Ext.onReady(function() {
    Ext.QuickTips.init();
    
    hide('#feedback div');
    feedback('no-time', true);
    
    Ext.get('hastime').select('input').on('click',function() {
        feedback('no-time', false);
        if (/yes/.exec(this.id)) {
            show('hasint','starttime','endtime');
            checkYesNo('hasint','no-int');
            checkSelect('start_type','no-type');
            checkYesNo('hasend', 'no-end');
        } else {
            hide('#hasint','#starttime','#endtime');
            feedback('*', false);
        }
    });
    
    Ext.get('hasint').select('.yesno input').on('click',function() {
        var input = Ext.get('presentation_strategy'), strategy = 'LIST';
        feedback('no-int', false);
        if (/yes/.exec(this.id)) {
            strategy = 'DISCRETE_INTERVAL';
            checkInterval();
            show('interval');
        } else {
            hide('#interval');
        }
        input.set({value: strategy});
    });
    
    Ext.get('precision_value').on('change', function() {
        checkInterval();
    })
    
    Ext.get('start_type').on('change',function() {
        checkSelect('start_type', 'no-type');
        var type = this.getValue(), selectID;
        hide("#start_att select");
        if (type == 'none') {            
            hide('#start_att');
        } else {
            selectID = "id_" + type + "_attribute";
            checkSelect(selectID, 'no-att');
            show('start_att',  selectID);
        }
        if (type == 'text') {
            show('startformat');
        } else {
            hide("#startformat");
        }
    });
    
    Ext.select('#start_att select').on('change', function() {
        checkSelect(this, 'no-att');
    });
    
    Ext.get('hasend').select('.yesno input').on('click',function() {
        feedback('no-end', false);
        if (/yes/.exec(this.id)) {
            checkSelect(Ext.get('end_type'), 'no-type');
            show('endtimeopts');
        } else {
            hide('#endtimeopts');
        }
    });
    
    Ext.get('end_type').on('change',function() {
        checkSelect(this, 'no-type');
        var type = this.getValue(), selectID;
        hide("#end_att select");
        if (type == 'none') {            
            hide('#end_att');
        } else {
            selectID = "id_end_" + type + "_attribute";
            checkSelect(selectID, 'no-att');
            show('end_att', selectID);
        }
        if (type == 'text') {
            show('endformat');
        } else {
            hide("#endformat");
        }
    });
    
    function checkInterval() {
        var intval = Ext.get('precision_value').getValue();
        feedback('no-int-mult', ! /^\d+$/.test(intval));
    }
     
    function checkYesNo(el, fid) {
        var checked = false;
        Ext.get(el).select('input').each(function(i) {
            checked |= i.getAttribute('checked');
        });
        feedback(fid, !checked);
    }
    
    function checkSelect(el, fid) {
        var val = Ext.get(el).getValue(), none = !val || /none/i.test(val);
        feedback(fid, none);
    }
    
    function hide() {
        for (var i = 0; i < arguments.length; i++) {
            Ext.select(arguments[i]).enableDisplayMode().hide();
        }
    }
    
    function show() {
        for (var i = 0; i < arguments.length; i++) {
            Ext.get(arguments[i]).removeClass('hide').show();
        }
    }

    function enableCustom(selectID, inputID, formatEl) {
        Ext.get(selectID).on('change',function() {
            var input = Ext.get(inputID);
            if (this.getAttribute('value') == '0') {
                formatEl.hide();
                input.dom.value = '';
            } else {
                formatEl.fadeIn();
                input.focus();
            }
        });
    }
    enableCustom('format_select','id_text_attribute_format',Ext.get('format_input'));
    enableCustom('end_format_select','id_end_text_attribute_format',Ext.get('end_format_input'));
    
    function feedback(id, on) {
        var any = false, divs = Ext.select('#feedback div');
        if (id != '*') {
            if (on) {
                Ext.get(id).show();
            } else {
                hide('#' + id);
            }
        } else {
            divs.enableDisplayMode().hide();
        }
        divs.each(function(i) {
            any |= i.isVisible() || i.isDisplayed();
        });
        Ext.get('feedback').setVisible(any);
        Ext.select('#timeForm input[type=submit]').setVisible(!any);
    }
    
    function checkAndClear(id, othersection) {
        var section = Ext.get(id);
        var clear = false;
        section.select('.yesno input').each(function(i) {
            if (i.getAttribute('checked')) {
                clear = i.id.indexOf('no') == 0;
            }
        });
        if (clear) {
            if (typeof othersection == 'string') {
                section = Ext.get(othersection);
            }
            section.select('input, select').each(function(i) {
                if ('value' in i.dom && i.dom.type != 'hidden') {
                    i.dom.value = '';
                } else {
                    i.dom.selectedIndex = 0;
                }
            });
        }
    }
    
    var timeForm = Ext.get('timeForm');
    // reset any cached values
    timeForm.dom.reset();
    // clear any values before submitting
    // this is not a standard way of adding this, but works around IE bug
    timeForm.beforeaction = function(ev) {
        checkAndClear('hastime','starttime');
        checkAndClear('hasint');
        checkAndClear('endtime');
    };
    
});