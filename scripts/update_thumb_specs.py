# contains functions to update specs/params
# useful for updating urls when migrating across domains

from geonode.maps.models import MapLayer
from geonode.maps.models import Thumbnail
from optparse import OptionParser
import sys

def make_updater(from_string, to_string, attr):
    """make an update function that given a model, fetches the attr,
    which must be a string, runs the string replace, and saves the
    model if the replace caused a change"""
    def updater(model):
        orig_value = getattr(model, attr)
        new_value = orig_value.replace(from_string, to_string)
        if orig_value != new_value:
            print 'updating %s %s' % (model._meta.object_name, model.id)
            setattr(model, attr, new_value)
            model.save()
    return updater

def make_thumbnail_updater(from_string, to_string):
    return make_updater(from_string, to_string, 'thumb_spec')

def make_maplayer_updater(from_string, to_string):
    return make_updater(from_string,  to_string, 'layer_params')

def update_thumbnail_specs(from_string, to_string):
    """run a string replace on all thumb specs from -> to"""
    updater = make_thumbnail_updater(from_string, to_string)
    for th in Thumbnail.objects.all():
        updater(th)

def update_maplayer_params(from_string, to_string):
    """run a string replace on all maplayer params"""
    updater = make_maplayer_updater(from_string, to_string)
    for ml in MapLayer.objects.all():
        updater(ml)


if __name__ == '__main__':
    parser = OptionParser('usage: %s from-string to-string' % sys.argv[0])
    parser.add_option('-t', '--thumbnails',
                      dest='update_thumbnails',
                      default=None,
                      action='store_true',
                      help='Update Thumbnails'
                      )
    parser.add_option('-m', '--maplayers',
                      dest='update_maplayers',
                      default=None,
                      action='store_true',
                      help='Update MapLayers',
                      )

    options, args = parser.parse_args()
    if len(args) != 2:
        parser.error('please specify the from-string and to-string to replace on thumb specs')
    if not (options.update_thumbnails or options.update_maplayers):
        parser.error('need to update thumbnails or maplayers')

    from_string, to_string = args

    if options.update_thumbnails:
        print 'updating thumbnails'
        update_thumbnail_specs(from_string, to_string)
    if options.update_maplayers:
        print 'updating maplayers'
        update_maplayer_params(from_string, to_string)
