# Updates existing map layer objects with new base layer names because
# of the way we store the base layer names, we need a script that
# updates the current configuration
import os
import argparse


# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "mapstory.settings"

from geonode.maps.models import MapLayer

name_mappings = {
    'Wayne': 'Naked Earth',
    'bluemarble': ' Satellite Imagery'
}


def rename_names(dry_run, original_name, new_name):
    queryset = MapLayer.objects.filter(name=original_name)
    if dry_run:
        print '%s layer(s) with the name %s would have been changed to %s' % (
            queryset.count(),
            original_name,
            new_name
        )
    else:
        print 'Updating %s with %s to %s' % (
            queryset.count(),
            original_name,
            new_name)
        queryset.update(name=new_name)


def main(args):
    dry_run = args.dry

    print 'Updating the currrent maps'
    if dry_run:
        print 'Running in dry mode'
        print 'This script will not change the database'

    rename_names(dry_run, 'bluemarble', 'Satellite Imagery')
    rename_names(dry_run, 'Wayne', 'Naked Earth')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--dry',
        help='Do a test run and not change the database',
        action='store_true'
    )
    args = parser.parse_args()
    main(args)
