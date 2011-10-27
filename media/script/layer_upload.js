function setup(csrf_token,form_target,userLookup) {
    Ext.onReady(function() {
        init(csrf_token,form_target,userLookup);
    });
}
function init(csrf_token,form_target,userLookup) {
    Ext.QuickTips.init();

    var xml_unsafe = /(^[^a-zA-Z\._]+)|([^a-zA-Z0-9\._])/g;
    var layer_title = new Ext.form.TextField({
      id: 'layer_title',
      fieldLabel: gettext('Title'),
      name: 'layer_title'
    });

    var listeners = {
        "fileselected": function(cmp, value) {
            // remove the path from the filename - avoids C:/fakepath etc.
            cmp.setValue(value.split(/[/\\]/).pop());
        }
    };

    var base_file = new Ext.ux.form.FileUploadField({
        id: 'base_file',
        emptyText: gettext('Select a layer data file'),
        fieldLabel: gettext('Data'),
        name: 'base_file',
        allowBlank: false,
        listeners: listeners
    });

    var dbf_file = new Ext.ux.form.FileUploadField({
        id: 'dbf_file',
        emptyText: gettext('Select a .dbf data file'),
        fieldLabel: gettext('DBF'),
        name: 'dbf_file',
        allowBlank: true,
        listeners: listeners,
        validator: function(name) {
            if ((name.length > 0) && (name.search(/\.dbf$/i) == -1)) {
                return gettext("Invalid DBF File.");
            } else {
                return true;
            }
        }
    });

    var shx_file = new Ext.ux.form.FileUploadField({
        id: 'shx_file',
        emptyText: gettext('Select a .shx data file'),
        fieldLabel: gettext('SHX'),
        name: 'shx_file',
        allowBlank: true,
        listeners: listeners,
        validator: function(name) {
            if ((name.length > 0) && (name.search(/\.shx$/i) == -1)) {
                return gettext("Invalid SHX File.");
            } else {
                return true;
            }
        }
    });

    var prj_file = new Ext.ux.form.FileUploadField({
        id: 'prj_file',
        emptyText: gettext('Select a .prj data file (optional)'),
        fieldLabel: gettext('PRJ'),
        name: 'prj_file',
        allowBlank: true,
        listeners: listeners,
        validator: function(name) {
            if ((name.length > 0) && (name.search(/\.prj$/i) == -1)) {
                return gettext("Invalid PRJ File.");
            } else {
                return true;
            }
        }
    });

    var sld_file = new Ext.ux.form.FileUploadField({
        id: 'sld_file',
        emptyText: gettext('Select a .sld style file (optional)'),
        fieldLabel: gettext('SLD'),
        name: 'sld_file',
        allowBlank: true,
        listeners: listeners
    });

    var abstractField = new Ext.form.TextArea({
        id: 'abstract',
        fieldLabel: gettext('Abstract'),
        name: 'abstract',
        allowBlank: true
    });

    var permissionsField = new Ext.form.Hidden({
        name: "permissions"
    });

    var fp = new Ext.FormPanel({
        renderTo: 'upload_form',
        fileUpload: true,
        width: 500,
        frame: true,
        autoHeight: true,
        unstyled: true,
        labelWidth: 50,
        defaults: {
            anchor: '95%',
            msgTarget: 'side'
        },
        items: [layer_title, base_file, dbf_file, shx_file, prj_file, sld_file, abstractField, permissionsField, {
            xtype: "hidden",
            name: "csrfmiddlewaretoken",
            value: csrf_token
        }],
        buttons: [{
            text: gettext('Upload'),
            handler: function(){
                if (fp.getForm().isValid()) {
                    fp.getForm().submit({
                        url: form_target,
                        waitMsg: gettext('Uploading your data...'),
                        success: function(fp, o) {
                            document.location = o.result.redirect_to;
                        },
                        failure: function(fp, o) {
                            error_message = '<ul>';
                            for (var i = 0; i < o.result.errors.length; i++) {
                                error_message += '<li>' + o.result.errors[i] + '</li>'
                            }
                            error_message += '</ul>'

                            Ext.Msg.show({
                                title: gettext("Error"),
                                msg: error_message,
                                minWidth: 200,
                                modal: true,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    });
                }
            }
        }]
    });

    var disable_shapefile_inputs = function() {
        dbf_file.hide();
        shx_file.hide();
        prj_file.hide();
    };

    var enable_shapefile_inputs = function() {
        dbf_file.show();
        shx_file.show();
        prj_file.show();
    };

    var check_shapefile = function() {
        if ((/\.shp$/i).test(base_file.getValue())) {
            enable_shapefile_inputs();
        } else {
            disable_shapefile_inputs();
        }
    };

    base_file.addListener('fileselected', function(cmp, value) {
        check_shapefile();
    });
    disable_shapefile_inputs();

    var permissionsEditor = new GeoNode.PermissionsEditor({
        renderTo: "permissions_form",
        userLookup: userLookup,
        listeners: {
            updated: function(pe) {
                permissionsField.setValue(Ext.util.JSON.encode(pe.writePermissions()));
            }
        },
        permissions: {
            anonymous: 'layer_readonly',
            authenticated: 'layer_readonly',
            users:[]
        }
    });
    permissionsEditor.fireEvent("updated", permissionsEditor);

    function test_file_api() {
        var fi = document.createElement('INPUT');
        fi.type = 'file';
        return 'files' in fi;
    }

    if (test_file_api()) {
        // track dropped files separately from values of input fields
        var dropped_files = {};
        // drop handler
        var drop = function(ev) {
            ev.preventDefault();
            dt = ev.dataTransfer, files = dt.files, i = 0;
            // this is the single file drop - it may be a tiff or a .shp file
            if (files.length == 1 && !dbf_file.isVisible()) {
                base_file.setValue(files[i].name);
                check_shapefile();
                dropped_files.base = files[i];
            } else {
                // multiple file drop
                for (; i < files.length; i++) {
                    var ext = files[i].name.split('.')[1];
                    if (ext == 'shp') {
                        base_file.setValue(files[i].name);
                        enable_shapefile_inputs();
                        dropped_files.base_file = files[i];
                    } else {
                        try {
                            var key = ext + '_file', w = eval(key);
                            w.setValue(files[i].name);
                            dropped_files[key] = files[i];
                        } catch (ReferenceError) {}
                    }
                }
            }
        };

        // drop target w/ drag over/exit effects
        var dropPanel = new Ext.Panel({
            html: "Drop Files Here",
            listeners: {
                render: function(p) {
                    var el = p.getEl().dom;
                    function t() { console.log('t'); p.body.toggleClass('x-grid3-cell-selected')};
                    el.addEventListener("dragover", function(ev) {
                        ev.stopPropagation();
                        ev.preventDefault();
                    }, true);
                    el.addEventListener("drop", function(ev) {
                        drop(ev);
                    },false);
                    el.addEventListener("dragexit",t);
                    el.addEventListener("dragenter",t);
                }
            }
        });
        fp.add(dropPanel);
        fp.doLayout();
        
        function createDragFormData() {
            var data = new FormData(), id, value, fields = fp.getForm().getFieldValues(), size = 0;
            for (id in fields) {
                value = fields[id];
                if (id in dropped_files) {
                    size = size + dropped_files[id].size;
                    data.append(id,dropped_files[id],value);
                } else {
                    data.append(id,value);
                }
            }
            return data;
        }

        function upload(formData) {
            var xhr = new XMLHttpRequest();
            var progress;

            xhr.upload.addEventListener('loadstart', function(ev) {
                progress = Ext.MessageBox.progress("Please wait","Uploading your data...");
            }, false);
            xhr.upload.addEventListener('progress', function(ev) {
                if (ev.lengthComputable) {
                    // assume that 25% of the time will be actual server work, not just upload time
                    progress.updateProgress( (ev.loaded/ev.total)* .75);
                    if (ev.loaded == ev.total) {
                        progress.updateProgress(.75,"Awaiting response");
                    }
                }
            }, false);

            function error(ev,result) {
                var error_message;
                if (typeof result != 'undefined') {
                    error_message = '<ul>';
                    for (var i = 0; i < result.errors.length; i++) {
                        error_message += '<li>' + result.errors[i] + '</li>'
                    }
                    error_message += '</ul>'
                } else {
                    error_message = "Unexpected Error:<p>" + xhr.responseText;
                }

                Ext.Msg.show({
                    title: gettext("Error"),
                    msg: error_message,
                    minWidth: 200,
                    modal: true,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
            xhr.addEventListener('load', function(ev) {
                try {
                    var result = Ext.decode(xhr.responseText);
                    if (result.success) {
                        document.location = result.redirect_to;
                    } else {
                        error(ev, result);
                    }
                } catch (ex) {
                    console.log(ex);
                    error(ev);
                }
            }, false);
            xhr.addEventListener('error', error, false);

            xhr.open("POST",form_target, true);
            xhr.send(formData);
        }

        fp.buttons[0].handler = function() {
            if (!fp.getForm().isValid()) return;
            upload(createDragFormData());
        }
 
    }
}