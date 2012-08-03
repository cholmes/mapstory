function setup(options) {
    Ext.onReady(function() {
        init(options);
    });
}
function init(options) {
    Ext.QuickTips.init();
    options = Ext.apply({
        is_featuretype : true,
        layer_name : null
    },options);

    var xml_unsafe = /(^[^a-zA-Z\._]+)|([^a-zA-Z0-9\._])/g;
    var layer_title;
    if (options.layer_name) {
        layer_title = new Ext.form.TextField({
            id: 'layer_name',
            name: 'layer_name',
            emptyText: options.layer_name,
            fieldLabel: gettext('Name'),
            allowBlank: true,
            disabled: true
        });
    } else {
        layer_title =  new Ext.form.TextField({
            id: 'layer_title',
            fieldLabel: gettext('Title'),
            name: 'layer_title'
        });
    }

    var listeners = {
        "fileselected": function(cmp, value) {
            // remove the path from the filename - avoids C:/fakepath etc.
            cmp.setValue(value.split(/[/\\]/).pop());
        }
    };
    var form_fields = [{
            xtype: "hidden",
            name: "csrfmiddlewaretoken",
            value: options.csrf_token
        }];

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
    
    function containerFromDom(id) {
        return new Ext.Container({
            contentEl : id
        });
    }
    
    var zipMsg = containerFromDom('zip-msg').hide();

    form_fields.push(base_file);
    form_fields.push(zipMsg);
    form_fields.push(sld_file);
    
    if (options.is_featuretype) {
        form_fields = form_fields.concat(dbf_file, shx_file, prj_file);
    }
    
    form_fields.push(containerFromDom('notes'));
    form_fields.push(containerFromDom('about-data'));
    
    form_fields.push(layer_title);
    if (!options.layer_name) {
        form_fields = form_fields.concat(abstractField,permissionsField);
    }
    
    function errorHandler(fp, o) {
        var html = '', msgs = Ext.get('form-messages');
        for (var i = 0; i < o.result.errors.length; i++) {
            html += '<li>' + o.result.errors[i] + '</li>'
        }
        msgs.query('ul')[0].innerHTML = html;
        msgs.slideIn('t');
    }

    var fp = new Ext.FormPanel({
        renderTo: 'upload_form',
        fileUpload: true,
        width: 600,
        frame: true,
        autoHeight: true,
        unstyled: true,
        labelWidth: 50,
        defaults: {
            anchor: '95%',
            msgTarget: 'side'
        },
        items: form_fields,
        buttons: [{
            text: gettext('Upload'),
            handler: function(){
                if (fp.getForm().isValid()) {
                    fp.getForm().submit({
                        url: options.form_target,
                        waitMsg: gettext('Uploading your data...'),
                        success: function(fp, o) {
                            document.location = o.result.redirect_to;
                        },
                        failure: errorHandler
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

    var checkFileType = function() {
        if ((/\.shp$/i).test(base_file.getValue())) {
            enable_shapefile_inputs();
        } else {
            disable_shapefile_inputs();
        }
        if ((/\.zip$/i).test(base_file.getValue())) {
            zipMsg.show();
        } else {
            zipMsg.hide();
        }
    };

    base_file.addListener('fileselected', function(cmp, value) {
        checkFileType();
    });
    
    if (options.layer_name) {
        enable_shapefile_inputs();
    } else {
        disable_shapefile_inputs();
    }

    if (! options.layer_name) {
        var permissionsEditor = new GeoNode.PermissionsEditor({
            renderTo: "permissions_form",
            userLookup: options.userLookup,
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
    }

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
            var dt = ev.dataTransfer, files = dt.files, i = 0, ext, key, w;
            // this is the single file drop - it may be a tiff or a shp file or a zip
            if (files.length == 1 && !dbf_file.isVisible()) {
                base_file.setValue(files[i].name);
                checkFileType();
                dropped_files.base_file = files[i];
            } else {
                // multiple file drop
                for (; i < files.length; i++) {
                    ext = files[i].name.split('.');
                    // grab the last part to avoid .shp.xml getting sucked in
                    ext = ext[ext.length - 1];
                    if (ext == 'shp') {
                        base_file.setValue(files[i].name);
                        enable_shapefile_inputs();
                        dropped_files.base_file = files[i];
                    } else {
                        try {
                            key = ext + '_file', w = eval(key);
                            w.setValue(files[i].name);
                            dropped_files[key] = files[i];
                        } catch (ReferenceError) {}
                    }
                }
            }
        };

        var dropTarget = Ext.get("drop-target");
        function t() {
            dropTarget.toggleClass('drop-hover');
        }
        Ext.get("drop-target").addListener("dragover", function(ev) {
            ev.stopPropagation();
            ev.preventDefault();
        }).addListener("drop", function(ev) {
            dropTarget.removeClass('drop-hover');
            drop(ev.browserEvent);
        }).addListener("dragexit",t).addListener("dragenter",t).setStyle('display','block');
        
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
                    var msg = parseInt(ev.loaded / 1024) + " of " + parseInt(ev.total / 1024);
                    progress.updateProgress( (ev.loaded/ev.total)* .75, msg);
                    if (ev.loaded == ev.total) {
                        progress.updateProgress(.75,"Awaiting response");
                    }
                }
            }, false);

            function error(ev,result) {
                var error_message;
                if (typeof result == 'undefined') {
                    result = ["Unexpected Error: " + xhr.responseText];
                }
                progress.hide();
                errorHandler(ev, {result:result});
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

            xhr.open("POST",options.form_target, true);
            xhr.send(formData);
        }

        var originalHandler = fp.buttons[0].handler;
        fp.buttons[0].handler = function() {
            if (!fp.getForm().isValid()) return;
            if ('base_file' in dropped_files) {
                upload(createDragFormData());
            } else {
                originalHandler();
            }
        }
    }
    
    Ext.select('.uip .icon-trash').on('click',function(ev) {
        ev.preventDefault();
        var a = new Ext.Element(this);
        Ext.Ajax.request({
            url : a.getAttribute('href'),
            success : function() {
                a.parent('.uip').slideOut('t',{useDisplay:true})
            },
            failure : function() {
                alert('Uh oh. An error occurred.')
            }
        })
    });
}
