from geonode.maps.models import Thumbnail
from optparse import OptionParser
import sys

def update_specs(from_string, to_string):
    """run a string replace on all thumb specs from -> to"""
    
    def update_spec(spec):
        return spec.replace(from_string, to_string)

    for th in Thumbnail.objects.all():
        orig_spec = th.thumb_spec
        new_spec = update_spec(orig_spec)
        th.thumb_spec = new_spec
        if orig_spec != new_spec:
            th.save()

if __name__ == '__main__':
    parser = OptionParser('usage: %s from-string to-string' % sys.argv[0])

    options, args = parser.parse_args()
    if len(args) != 2:
        parser.error('please specify the from-string and to-string to replace on thumb specs')

    update_specs(args[0], args[1])
