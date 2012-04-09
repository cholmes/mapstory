# export list of maps/layers/maplayer objects that can be used for import script

from django.core import serializers
from django.conf import settings

from geonode.maps.models import *

from optparse import OptionParser
import psycopg2
import sys
import os
import tempfile
import re
import shutil

from export_layer import export_layer

gs_data_dir = '/var/lib/geoserver/geonode-data/'

parser = OptionParser('usage: %s [options] maps_export_file.zip' % sys.argv[0])
parser.add_option('-d', '--data-dir',
                  dest='data_dir',
                  default=gs_data_dir,
                  help='geoserver data dir')
parser.add_option('-i', '--input-file',
                  dest='input_file',
                  help='Input file that contains the list of maps and '
                  'layers to export. It should contain one url per '
                  'line. The url is parsed to determine whether the '
                  'entry is a map or layer.',
                  )

(options, args) = parser.parse_args()
if len(args) != 1:
    parser.error('please provide the export map zip file')
if not options.input_file:
    parser.error('please provide the input file containing the '
                 'maps/layers to export')

gs_data_dir = options.data_dir

gspath = lambda *p: os.path.join(gs_data_dir, *p)

map_ids = set()
layer_names = set()

with open(options.input_file) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        m = re.search(r'/maps/(\d+)$', line)
        if m:
            map_ids.add(m.group(1))
        else:
            m = re.search(r'/data/(geonode:.*)$', line)
            if m:
                layer_names.add(m.group(1))
            else:
                raise ValueError('Unknown input line: %s' % line)

# fetch maps and layers from database
def fetch_map(map_id):
    try:
        return Map.objects.get(pk=map_id)
    except Map.DoesNotExist:
        print 'No map found with id: %s' % map_id
        return None

def fetch_layer(layer_name):
    try:
        return Layer.objects.get(typename=layer_name)
    except Layer.DoesNotExist:
        print 'No layer found with name: %s' % layer_name
        return None

maps = filter(None, map(fetch_map, map_ids))
layers = filter(None, map(fetch_layer, layer_names))
maplayers = sum([m.layers for m in maps], [])

def layers_from_map(m):
    layers = []
    for maplayer in m.layers:
        # is this right?
        if maplayer.ows_url:
            layer = Layer.objects.get(typename=maplayer.name)
            layers.append(layer)
    return layers

# get a list of all layers to export
# this is all the layers from all maps, combined with all layers specified
# also make them unique to avoid duplicates
all_layers = sum(map(layers_from_map, maps), []) + layers
unique_layers_map = dict((l.id, l) for l in all_layers)
layers_to_export = unique_layers_map.values()

# create the layout for the uber zip file that will contain the maps/layers underneath
tempdir = tempfile.mkdtemp()

temppath = lambda *args: os.path.join(tempdir, *args)

layersdir = os.path.join(tempdir, 'layers')
os.mkdir(layersdir)

# keep track of where we are
curdir = os.getcwd()

# connect to database for layer export
conn = psycopg2.connect("dbname='" + settings.DB_DATASTORE_DATABASE + 
                        "' user='" + settings.DB_DATASTORE_USER + 
                        "' password='" + settings.DB_DATASTORE_PASSWORD + 
                        "' port=" + settings.DB_DATASTORE_PORT + 
                        " host='" + settings.DB_DATASTORE_HOST + "'")

# export all the layers
for layer in layers_to_export:
    layerdirpath = os.path.join(layersdir, layer.name)
    os.mkdir(layerdirpath)
    export_layer(gs_data_dir, conn, layerdirpath, layer)

# export the maps and the maplayers
def export_json(path, data):
    with open(path, 'w') as out:
        serializers.serialize('json', data, stream=out)

export_json(temppath('maps.json'), maps)
export_json(temppath('maplayers.json'), maplayers)

# create the uber zip
zipfilename = args[0]
os.chdir(tempdir)
os.system('zip -r %s .' % zipfilename)

# move the zip file to the current directory
os.chdir(curdir)
shutil.move(os.path.join(tempdir, zipfilename), zipfilename)

conn.close()
