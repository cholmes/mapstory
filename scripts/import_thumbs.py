from geonode.maps.models import Map
from optparse import OptionParser
import json
import sys

def import_thumbs(inputstream):
    # format is a list of (mapid, [serialized-django-thumb])

    input_data = json.load(inputstream)
    for mapid, thumb_spec in input_data:
        try:
            m = Map.objects.get(pk=mapid)
        except Map.DoesNotExist:
            print 'no map with id: %s' % mapid
        else:
            existing_thumbnail = m.get_thumbnail()
            if existing_thumbnail:
                print 'thumbnail already exists for %s ... skipping' % mapid
            else:
                m.set_thumbnail(thumb_spec)

if __name__ == '__main__':
    parser = OptionParser('usage: %s [options] json-filename' % sys.argv[0])

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("please provide the json filename")

    with open(args[0]) as inputstream:
        import_thumbs(inputstream)
