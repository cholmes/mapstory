# export list of maps/layers/maplayer objects that can be used for import script

from django.core import serializers
from django.conf import settings

from optparse import OptionParser
import psycopg2
import sys
import os
import tempfile

from import_layer import import_layer

def import_maps(gs_data_dir, conn, zipfile, no_password=False, chown_to=None):
    tempdir = tempfile.mkdtemp()
    temppath = lambda *p: os.path.join(tempdir, *p)
    os.system('unzip %s -d %s' % (zipfile, tempdir))

    for layer_name in os.listdir(temppath('layers')):
        import_layer(gs_data_dir, conn,
                     temppath('layers', layer_name), layer_name,
                     no_password, chown_to)

    def import_models(path):
        with open(path, 'r') as f:
            models = serializers.deserialize('json', f)
            for model in models:
                model.save()

    import_models(temppath('maps.json'))
    import_models(temppath('maplayers.json'))

if __name__ == '__main__':
    gs_data_dir = '/var/lib/geoserver/geonode-data/'
    parser = OptionParser('usage: %s [options] maps_import_file.zip' % sys.argv[0])
    parser.add_option('-d', '--data-dir',
                      dest='data_dir',
                      default=gs_data_dir,
                      help='geoserver data dir')

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error('please provide the maps import zip file')

    conn = psycopg2.connect("dbname='" + settings.DB_DATASTORE_DATABASE + 
                            "' user='" + settings.DB_DATASTORE_USER + 
                            "' password='" + settings.DB_DATASTORE_PASSWORD + 
                            "' port=" + settings.DB_DATASTORE_PORT + 
                            " host='" + settings.DB_DATASTORE_HOST + "'")

    zipfile = args[0]
    import_maps(options.data_dir, conn, zipfile)
    conn.commit()
    conn.close()
