# read in a mapstory json dump (from manage.py dumpdata mapstory) and
# write out a new json dump with missing layer and map ids removed
# this should be run on the machine that will be loading the json dump

from optparse import OptionParser
import json
import sys

from geonode.maps.models import Layer
from geonode.maps.models import Map

parser = OptionParser('usage: %s [options] mapstory.json' % sys.argv[0])
options, args = parser.parse_args()
if len(args) != 1:
    parser.error("please provide the mapstory json file created with "
                 "manage.py dumpdata mapstory")

jsonfile = args[0]

def model_exists(object_manager):
    return lambda object_id: bool(object_manager.filter(pk=object_id))

def convert_model(model):
    model_type = model.get('model')
    if model_type != 'mapstory.topic':
        return model
    fields = model['fields']
    fields['layers'] = filter(model_exists(Layer.objects), fields['layers'])
    fields['maps'] = filter(model_exists(Map.objects), fields['maps'])
    model['fields'] = fields
    return model
    
with open(jsonfile) as inputstream:
    json.dump(map(convert_model, json.load(inputstream)),
              sys.stdout)
