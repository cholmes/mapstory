# Updates existing map layer objects with new base layer names because
# of the way we store the base layer names, we need a script that
# updates the current configuration
import os
import argparse


# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "mapstory.settings"


from geonode.maps.models import Map
from geonode.maps.models import MapLayer

name_mappings = {
    'Wayne': 'Naked Earth',
    'bluemarble': ' Satellite Imagery'
}


def fix_names(args):
    dry_run = args.dry

    print 'Updating the currrent maps'
    if dry_run:
        print 'This script will not change the database'

    for m in Map.objects.all():
        for layer in MapLayer.objects.filter(map=m.id):
            if not layer.local():
                if layer.name in name_mappings:
                    new_name = name_mappings[layer.name]
                    if not dry_run:
                        print 'Replacing %s with %s' % (layer.name, new_name)
                        layer.name = new_name
                    else:
                        print 'Dry run, nothing will be changed'
                        print 'However would have replaced %s with %s' % (
                            layer.name, new_name
                        )
                else:
                    print 'The base layer name should be correct'
                    print 'Base layer name is -> %s ' % layer.name


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dry',
        help='Do a test run and not change the database',
        type=bool,
        default=True
    )
    args = parser.parse_args()
    fix_names(args)
