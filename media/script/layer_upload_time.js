Ext.onReady(function() {
    Ext.QuickTips.init();
    
    hide('#feedback div');
    
    Ext.get('hastime').select('input').on('click',function() {
        if (/yes/.exec(this.id)) {
            show('hasint','starttime','endtime');
        } else {
            hide('#hasint','#starttime','#endtime');
        }
    });
    
    Ext.get('hasint').select('.yesno input').on('click',function() {
        var input = Ext.get('presentation_strategy'), strategy = 'LIST';
        if (/yes/.exec(this.id)) {
            strategy = 'DISCRETE_INTERVAL';
            show('interval');
        } else {
            hide('#interval');
        }
        input.set({value: strategy});
    });
    
    Ext.get('start_type').on('change',function() {
        var type = this.getValue(), selectID;
        hide("#start_att select");
        if (type == 'none') {            
            hide('#start_att');
        } else {
            selectID = "id_" + type + "_attribute";
            show('start_att',  selectID);
        }
        if (type == 'text') {
            show('startformat');
        } else {
            hide("#startformat");
        }
    });
    
    Ext.get('hasend').select('.yesno input').on('click',function() {
        if (/yes/.exec(this.id)) {
            show('endtimeopts');
        } else {
            hide('#endtimeopts');
        }
    });
    
    Ext.get('end_type').on('change',function() {
        var type = this.getValue(), selectID;
        hide("#end_att select");
        if (type == 'none') {            
            hide('#end_att');
        } else {
            selectID = "id_end_" + type + "_attribute";
            show('end_att', selectID);
        }
        if (type == 'text') {
            show('endformat');
        } else {
            hide("#endformat");
        }
    });
    
    function validate() {
        var val = yesNoValue('hastime'), feedback = [], i, attType;
       
        if (val == null) {
            feedback.push('no-time');
        }
        if (val) {
            val = yesNoValue('hasint');
            if (val == null) {
                feedback.push('no-int');
            } else if (val) {
                if (!checkInterval()) {
                    feedback.push('no-int-mult');
                }
            }
            
            attType = Ext.get('start_type').getValue();
            if (attType == 'none') {
                feedback.push('no-type-start');
            } else {
                val = Ext.get("id_" + attType + "_attribute").getValue();
                if (!val) {
                    feedback.push('no-startatt');
                }
                if (attType == 'text') {
                    val = Ext.get('format_select').getValue();
                    if (val == '0') {
                        feedback.push('no-format-type-start')
                    } else if (val == '2') {
                        val = Ext.get('id_text_attribute_format').getValue();
                        if (!val) {
                            feedback.push('no-startformat');
                        }
                    }
                }
            }
            
            val = yesNoValue('hasend');
            if (val == null) {
                feedback.push('no-end');
            } else if (val) {
                attType = Ext.get('end_type').getValue();
                if (attType == 'none') {
                    feedback.push('no-type-end');
                } else {
                    val = Ext.get("id_end_" + attType + "_attribute").getValue();
                    if (!val) {
                        feedback.push('no-endatt');
                    }
                    if (attType == 'text') {
                        val = Ext.get('format_select').getValue();
                        if (val == '0') {
                            feedback.push('no-format-type-end').getValue();
                        } else if (val == '2') {
                            val = Ext.get('id_end_text_attribute_format').getValue();
                            if (!val) {
                                feedback.push('no-endformat');
                            }
                        }
                    }
                }
            }
        }
        if (feedback.length > 0) {
            show('feedback');
        } else {
            hide('#feedback');
        }
        hide('#feedback div');
        for (i = 0; i < feedback.length; i++) {
            Ext.get(feedback[i]).enableDisplayMode().show();
        }
        return feedback.length == 0;
    }
    
    function yesNoValue(el) {
        var checked = null;
        Ext.get(el).select('input').each(function(i) {
            if (i.getAttribute('checked')) {
                checked = i.id.indexOf('yes') == 0;
            }
        });
        return checked;
    }
    
    function checkInterval() {
        var intval = Ext.get('precision_value').getValue();
        return /^\d+$/.test(intval);
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
            if (this.getAttribute('value') == '2') {
                formatEl.fadeIn();
                input.focus();
            } else {
                formatEl.hide();
                input.dom.value = '';
            }
        });
    }
    enableCustom('format_select','id_text_attribute_format',Ext.get('format_input'));
    enableCustom('end_format_select','id_end_text_attribute_format',Ext.get('end_format_input'));
   
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
    // clear any values before submitting
    // this is not a standard way of adding this, but works around IE bug
    timeForm.beforeaction = function() {
        if (!validate()) {
            return false;
        }
        checkAndClear('hastime','starttime');
        checkAndClear('hasint');
        checkAndClear('endtime');
    };
    
});