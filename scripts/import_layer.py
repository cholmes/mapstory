'''Import an extracted layer and related resources'''
import os.path
from django.core import serializers

from geonode.maps.models import *

import psycopg2
import sys
import os
import tempfile
import shutil

gs_data_dir = '/var/lib/geoserver/geonode-data/'

args = sys.argv[1:]
if not args:
    print 'please provide a layer extract zip file'
    sys.exit(1)
if '-d' in args:
    idx = args.index('-d')
    args.pop(idx)
    gs_data_dir = args.pop(idx) 
    
gspath = lambda *p: os.path.join(gs_data_dir, *p)
    
zipfile = args.pop()
layer_name = zipfile[:zipfile.rindex('-extract')]

tempdir = tempfile.mkdtemp()
temppath = lambda *p: os.path.join(tempdir, *p)
os.system('unzip %s -d %s' % (zipfile, tempdir))

# can't check return value since pg_restore will complain if any drop statements fail :(
retval = os.system('pg_restore --dbname=%s --clean --username=%s < %s' % (
    settings.DB_DATASTORE_DATABASE, settings.DB_DATASTORE_USER, temppath('layer.dump')
))

# rebuild the geometry columns entry
with open(temppath("geom.info")) as fp:
    geom_cols = eval(fp.read())[0]
    
conn = psycopg2.connect("dbname='" + settings.DB_DATASTORE_DATABASE + 
                        "' user='" + settings.DB_DATASTORE_USER + 
                        "' password='" + settings.DB_DATASTORE_PASSWORD + 
                        "' port=" + settings.DB_DATASTORE_PORT + 
                        " host='" + settings.DB_DATASTORE_HOST + "'")
cursor = conn.cursor()
# f_table_catalog, f_table_schema, f_table_name
cursor.execute("delete from geometry_columns where f_table_schema='%s' and f_table_name='%s'" % (geom_cols[1],geom_cols[2]))
cursor.execute('insert into geometry_columns VALUES(%s)' % ','.join(["'%s'" % v for v in geom_cols]))

#copy in styles
for f in os.listdir(temppath('styles')):
    shutil.copy(temppath('styles',f),gspath('styles'))

# and other geoserver info
for ws in os.listdir(temppath('workspaces')):
    for store_name in os.listdir(temppath('workspaces',ws)):
        for layer_name in os.listdir(temppath('workspaces',ws,store_name)):
            dest_dir = gspath('workspaces', ws, store_name, layer_name)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            fdir = temppath('workspaces', ws, store_name, layer_name)
            for f in os.listdir(fdir):
                shutil.copy(os.path.join(fdir,f), dest_dir)
        
# reload catalog
Layer.objects.gs_catalog.http.request(settings.GEOSERVER_BASE_URL + "rest/reload",'POST')

# now we can create the django model - must be done last when gscatalog is ready
with open(temppath("model.json")) as fp:
    layer = serializers.deserialize("json", fp.read()).next()
layer.save()

shutil.rmtree(tempdir)