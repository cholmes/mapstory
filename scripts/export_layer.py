'''Extract a layer and relevant resources'''
from django.core import serializers
from django.conf import settings

from geonode.maps.models import *

import psycopg2
import sys
import os
import tempfile
import shutil

def export_layer(gs_data_dir, tempdir, layer):
    gslayer = Layer.objects.gs_catalog.get_layer(layer.typename)
    gsresource = gslayer.resource

    temppath = lambda *p: os.path.join(tempdir, *p)
    gspath = lambda *p: os.path.join(gs_data_dir, *p)

    conn = psycopg2.connect("dbname='" + settings.DB_DATASTORE_DATABASE + 
                            "' user='" + settings.DB_DATASTORE_USER + 
                            "' password='" + settings.DB_DATASTORE_PASSWORD + 
                            "' port=" + settings.DB_DATASTORE_PORT + 
                            " host='" + settings.DB_DATASTORE_HOST + "'")
    cursor = conn.cursor()

    #dump db table - this gets the table schema, too
    dump_cmd = 'pg_dump -f %s --format=c --create --table=\\"%s\\" --username=%s %s' % (
        os.path.join(tempdir, 'layer.dump'), gsresource.name, settings.DB_DATASTORE_USER, settings.DB_DATASTORE_DATABASE)
    retval = os.system(dump_cmd)
    if retval != 0:
        print dump_cmd
        print 'failed!'
        sys.exit(1)

    #get the geometry_columns entry
    cursor.execute("select * from geometry_columns where f_table_name='%s'" % layer.name)
    with open(temppath('geom.info'),'wb') as fp:
        fp.write(str(cursor.fetchall()))
    
    #dump django Layer object
    with open(temppath('model.json'),'wb') as fp:
        fp.write(serializers.serialize("json", [layer]))

    layer_name = layer.name
    #copy geoserver layer info
    workspace_path = 'workspaces/%s/%s/%s' % (gsresource.workspace.name, gsresource.store.name, layer_name)
    os.makedirs(temppath(workspace_path))
    for f in os.listdir(gspath(workspace_path)):
        shutil.copy(gspath(workspace_path,f), temppath(workspace_path,f))

    os.makedirs(temppath('styles'))
    def copy_style(style):
        if not style: return
        shutil.copy(gspath('styles',style.name + ".sld"), temppath('styles'))
        shutil.copy(gspath('styles',style.name + ".xml"), temppath('styles'))

    #gather styles
    copy_style(gslayer.default_style)
    map(copy_style, gslayer.styles)

    # zip files
    curdir = os.getcwd()
    os.chdir(tempdir)
    os.system('zip -r %s/%s-extract.zip .' % (curdir,layer_name))

if __name__ == '__main__':
    gs_data_dir = '/var/lib/geoserver/geonode-data/'

    args = sys.argv[1:]
    if not args:
        print 'use: extract_layer.py [-d gs_data_dir] layername'
        sys.exit(1)
    if '-d' in args:
        idx = args.index('-d')
        args.pop(idx)
        gs_data_dir = args.pop(idx) 
    
    layer_name = args.pop()
    try:
        layer = Layer.objects.get(name=layer_name)
    except Layer.DoesNotExist:
        print 'no such layer'
        sys.exit(1)

    tempdir = tempfile.mkdtemp()

    export_layer(tempdir, layer)

    # and cleanup
    shutil.rmtree(tempdir)
