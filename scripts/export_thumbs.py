from django.core.serializers import serialize
from geonode.maps.models import Map
from optparse import OptionParser
import json
import sys

def export_thumbs(maps, outputstream):
    # output json will be a list of tuples of
    # (mapid, [django serialized thumbnail object])
    output_data = []
    for m in maps:
        th = m.get_thumbnail()
        if th:
            serialized_thumb = serialize('json', [th])
            output_data.append((m.id, serialized_thumb))
        else:
            print 'Map: %s has no thumbnail' % m.id
    json.dump(output_data, outputstream)

def read_map_from_id(mapid):
    try:
        return Map.objects.get(pk=mapid)
    except Map.DoesNotExist:
        print 'No map found with id: %s' % mapid

def read_maps(stream):
    maps = []
    for line in stream:
        line = line.strip()
        m = read_map_from_id(int(line))
        if m:
            maps.append(m)
    return maps

if __name__ == '__main__':
    parser = OptionParser('usage: %s [options] json-filename' % sys.argv[0])
    parser.add_option('-i', '--input-file',
                      dest='input_file',
                      help='Input file that contains a list of map ids')

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("please provide the json filename")
    if not options.input_file:
        parser.error('please provide the input file containing the map ids')

    with open(options.input_file) as mapids_stream:
        maps = read_maps(mapids_stream)
        with open(args[0], 'w') as output_json_stream:
            export_thumbs(maps, output_json_stream)
