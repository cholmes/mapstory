'''Extract a layer and relevant resources'''
from django.core import serializers
from django.conf import settings

from geonode.maps.models import Layer

from mapstory.models import PublishingStatus

import json
import psycopg2
import sys
import os
import tempfile
import shutil
import xml.dom.minidom

def export_layer(gs_data_dir, conn, tempdir, layer):
    gslayer = Layer.objects.gs_catalog.get_layer(layer.typename)
    gsresource = gslayer.resource

    # fetch the nativeName, the name of the table in the database
    # which is not necessarily the same name as the layer
    gsresource.fetch()
    nativeName = gsresource.dom.find('nativeName').text

    temppath = lambda *p: os.path.join(tempdir, *p)
    gspath = lambda *p: os.path.join(gs_data_dir, *p)

    cursor = conn.cursor()

    #dump db table - this gets the table schema, too
    dump_cmd = 'pg_dump -f %s --format=c --create --table=\\"%s\\" --username=%s %s' % (
        os.path.join(tempdir, 'layer.dump'), nativeName, settings.DB_DATASTORE_USER, settings.DB_DATASTORE_DATABASE)
    retval = os.system(dump_cmd)
    if retval != 0:
        print dump_cmd
        print 'failed!'
        sys.exit(1)

    #get the geometry_columns entry
    cursor.execute("select * from geometry_columns where f_table_name='%s'" % nativeName)
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
    def parse_sld_filename(stylexmlpath):
        with open(stylexmlpath) as f:
            dom = xml.dom.minidom.parse(f)
            filename = dom.getElementsByTagName('filename')
            if filename:
                return filename[0].firstChild.nodeValue;

    def copy_style(style):
        if not style: return
        xmlfilepath = gspath('styles',style.name + ".xml")
        sld_filename = parse_sld_filename(xmlfilepath)
        shutil.copy(xmlfilepath, temppath('styles'))
        if not sld_filename:
            print 'Could not parse sld filename from: %s' % xmlfilepath
        else:
            shutil.copy(gspath('styles', sld_filename), temppath('styles'))

    #gather styles
    copy_style(gslayer.default_style)
    map(copy_style, gslayer.styles)

    # dump out thumb_spec if exists
    t = layer.get_thumbnail()
    if t:
        with open(temppath('thumb_spec.json'), 'w') as f:
            json.dump(t.thumb_spec, f)
    
    try:
        pubstat = PublishingStatus.objects.get(layer=layer)
        with open(temppath('publishingstatus.json'), 'w') as f:
            serializers.serialize('json', [pubstat], stream=f)
    except PublishingStatus.DoesNotExist:
        print 'No publishing status found for layer: %s' % layer

    cursor.close()

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
    
    conn = psycopg2.connect("dbname='" + settings.DB_DATASTORE_DATABASE + 
                            "' user='" + settings.DB_DATASTORE_USER + 
                            "' password='" + settings.DB_DATASTORE_PASSWORD + 
                            "' port=" + settings.DB_DATASTORE_PORT + 
                            " host='" + settings.DB_DATASTORE_HOST + "'")

    layer_name = args.pop()
    try:
        layer = Layer.objects.get(name=layer_name)
    except Layer.DoesNotExist:
        print 'no such layer'
        sys.exit(1)

    tempdir = tempfile.mkdtemp()

    # creates the layer layout structure in the temp directory
    export_layer(gs_data_dir, conn, tempdir, layer)

    # zip files
    curdir = os.getcwd()
    os.chdir(tempdir)
    os.system('zip -r %s/%s-extract.zip .' % (curdir,layer_name))

    # and cleanup
    shutil.rmtree(tempdir)
    conn.close()
