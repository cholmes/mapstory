# export list of maps/layers/maplayer objects that can be used for import script

from django.core import serializers
from django.conf import settings
from django.contrib.auth.models import User

from optparse import OptionParser
import psycopg2
import sys
import os
import tempfile

from import_layer import import_layer

def import_maps(gs_data_dir, conn, zipfile,
                no_password=False, chown_to=None, do_django_layer_save=True):
    tempdir = tempfile.mkdtemp()
    temppath = lambda *p: os.path.join(tempdir, *p)
    os.system('unzip %s -d %s' % (zipfile, tempdir))

    for layer_name in os.listdir(temppath('layers')):
        import_layer(gs_data_dir, conn,
                     temppath('layers', layer_name), layer_name,
                     no_password, chown_to, do_django_layer_save)
        conn.commit()

    print 'layers import complete'

    def import_models(path, add_owner=False):
        with open(path, 'r') as f:
            models = serializers.deserialize('json', f)
            for model in models:
                if add_owner:
                    owner = User.objects.filter(pk=model.object.owner_id)
                    if not owner:
                        model.object.owner = User.objects.get(pk=1)

                model.save()

    print 'importing maps'
    import_models(temppath('maps.json'), add_owner=True)
    print 'importing map layers'
    import_models(temppath('maplayers.json'))

if __name__ == '__main__':
    gs_data_dir = '/var/lib/geoserver/geonode-data/'
    parser = OptionParser('usage: %s [options] maps_import_file.zip' % sys.argv[0])
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
    parser.add_option('-L', '--skip-django-layer-save',
                      dest='do_django_layer_save',
                      default=True,
                      action='store_false',
                      help='Whether to skip loading the django layer models'
                      )

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error('please provide the maps import zip file')

    conn = psycopg2.connect("dbname='" + settings.DB_DATASTORE_DATABASE + 
                            "' user='" + settings.DB_DATASTORE_USER + 
                            "' password='" + settings.DB_DATASTORE_PASSWORD + 
                            "' port=" + settings.DB_DATASTORE_PORT + 
                            " host='" + settings.DB_DATASTORE_HOST + "'")

    zipfile = args[0]
    import_maps(options.data_dir, conn, zipfile,
                options.no_password, options.chown_to,
                options.do_django_layer_save)
    conn.commit()
    conn.close()
