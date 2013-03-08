# export list of maps/layers/maplayer objects that can be used for import script

from django.core import serializers
from django.conf import settings

from geonode.maps.models import Layer
from geonode.maps.models import Map

from mapstory.models import User
from mapstory.models import PublishingStatus

from dialogos.models import Comment

from optparse import OptionParser
import json
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

# fetch maps, layers and map comments from database
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

def fetch_map_comments(map):
    map_comments = Comment.objects.filter(object_id=map.id)
    if len(map_comments) == 0:
        return None
    else:
        return map_comments

def fetch_author(comment):
    try:
        return comment.author
    except User.DoesNotExist:
        print 'No user found for comment: %s' % comment
        return None

def fetch_map_publishingstatus(map):
    try:
        return PublishingStatus.objects.get(map=map)
    except PublishingStatus.DoesNotExist:
        print 'No publishing status found for map: %s' % map
        return None

maps = filter(None, map(fetch_map, map_ids))
layers = filter(None, map(fetch_layer, layer_names))
maplayers = sum([m.layers for m in maps], [])
map_comments = map(fetch_map_comments, maps)
authors = filter(None, map(fetch_author, [map_comment for sublist in map_comments for map_comment in sublist]))
publishing_statuses = map(fetch_map_publishingstatus, maps)

def layers_from_map(m):
    layers = []
    for maplayer in m.layers:
        try:
            layer = Layer.objects.get(typename=maplayer.name)
            layers.append(layer)
        except Layer.DoesNotExist:
            pass
    # also include the annotations layer if it exists
    annotation_layer_typename = "geonode:_map_%s_annotations" % m.id
    try:
        annotation_layer = Layer.objects.get(typename=annotation_layer_typename)
        layers.append(annotation_layer)
    except Layer.DoesNotExist:
        pass
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

# export map thumb specs
# list of (map_id, thumb_specs)
def map_thumb_spec(m):
    t = m.get_thumbnail()
    return t and (m.id, t.thumb_spec)

map_thumbs = filter(None, map(map_thumb_spec, maps))
with open(temppath('map_thumb_specs.json'), 'w') as f:
    json.dump(map_thumbs, f)

# export the map comments
# the comments won't serialize with json. have to use django serializer
JOSNSerializer = serializers.get_serializer("json")
json_serializer = JOSNSerializer()
with open(temppath('map_comments.json'), 'w') as f:
    json_serializer.serialize([map_comment for sublist in map_comments for map_comment in sublist], stream=f)

# export the comment authors
with open(temppath('comment_users.json'), 'w') as f:
    json_serializer.serialize(authors, stream=f)

# export the maps' publishing_statuses
with open(temppath('map_publishing_status.json'), 'w') as f:
    json_serializer.serialize(publishing_statuses, stream=f)

# create the uber zip
zipfilename = args[0]
os.chdir(tempdir)
os.system('zip -r %s/%s .' % (curdir, zipfilename))

conn.close()
shutil.rmtree(tempdir)
