'''Import an extracted layer and related resources'''
from django.conf import settings
from django.contrib.auth.models import User
from django.core import serializers

from geonode.maps.models import Layer

from optparse import OptionParser
import psycopg2
import os
import tempfile
import shutil

def import_layer(gs_data_dir, conn, layer_tempdir, layer_name,
                 no_password=False, chown_to=None):

    print 'importing layer: %s' % layer_name
    gspath = lambda *p: os.path.join(gs_data_dir, *p)

    temppath = lambda *p: os.path.join(layer_tempdir, *p)

    restore_string = 'pg_restore --host=%s --dbname=%s --clean --username=%s %s < %s' % (
        settings.DB_DATASTORE_HOST, settings.DB_DATASTORE_DATABASE, settings.DB_DATASTORE_USER,
        no_password and '--no-password' or '',
        temppath('layer.dump'),
    )
    # can't check return value since pg_restore will complain if any drop statements fail :(
    os.system(restore_string)

    # rebuild the geometry columns entry
    with open(temppath("geom.info")) as fp:
        s = fp.read()
        geom_cols = eval(s)[0]
        
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
            
    if chown_to:
        from pwd import getpwnam
        userid = getpwnam(chown_to)[2]
        for root, dirs, files in os.walk(gspath()):
            os.chown(root, userid, -1)
            for f in files:
                os.chown(os.path.join(root, f), userid, -1)

    # reload catalog
    Layer.objects.gs_catalog.http.request(settings.GEOSERVER_BASE_URL + "rest/reload",'POST')

    # now we can create the django model - must be done last when gscatalog is ready
    with open(temppath("model.json")) as fp:
        json = fp.read()
        layer = serializers.deserialize("json", json).next()
        owner = User.objects.filter(pk=layer.object.owner_id)
        if not owner:
            layer.object.owner = User.objects.get(pk=1)
        layer_exists = Layer.objects.filter(typename=layer.object.typename)
        if not layer_exists:
            layer.save()

    cursor.close()

if __name__ == '__main__':
    gs_data_dir = '/var/lib/geoserver/geonode-data/'

    parser = OptionParser('usage: %s [options] layer_import_file.zip')
    parser.add_option('-d', '--data-dir',
                      dest='data_dir',
                      default=gs_data_dir,
                      help='geoserver data dir')
    parser.add_option('-P', '--no-password',
                      dest='no_password', action='store_true',
                      help='Add the --no-password option to the pg_restore'
                      'command. This assumes the user has a ~/.pgpass file'
                      'with the credentials. See the pg_restore man page'
                      'for details.',
                      default=False,
                      )
    parser.add_option('-c', '--chown-to',
                      dest='chown_to',
                      help='If set, chown the files copied into the'
                      'geoserver data directory to a particular'
                      'user. Assumes the user running is root or has'
                      'permission to do so. This is useful to chown the'
                      'files to something like tomcat6 afterwards.',
                      )

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error('please provide a layer extract zip file')

    conn = psycopg2.connect("dbname='" + settings.DB_DATASTORE_DATABASE + 
                            "' user='" + settings.DB_DATASTORE_USER + 
                            "' password='" + settings.DB_DATASTORE_PASSWORD + 
                            "' port=" + settings.DB_DATASTORE_PORT + 
                            " host='" + settings.DB_DATASTORE_HOST + "'")

    zipfile = args.pop()
    tempdir = tempfile.mkdtemp()
    layer_name = zipfile[:zipfile.rindex('-extract')]
    os.system('unzip %s -d %s' % (zipfile, tempdir))

    import_layer(options.data_dir, conn, tempdir, layer_name,
                 options.no_password, options.chown_to)

    shutil.rmtree(tempdir)
    conn.commit()
    conn.close()
