from watchdog.core import *
from geonode.maps.models import Layer
from django.conf import settings
import functools
from urllib import urlopen

def suite():
    return get_capabilities, get_layer_capabilities
    
@check
def get_capabilities():
    Layer.objects.get_wms()
    
@check_many
def get_layer_capabilities():
    for l in Layer.objects.all().iterator():
        func = functools.partial(_check_layer, l)
        func.__name__ = l.typename
        yield func
            
def _check_layer(layer):
    try:
        layer.metadata()
        return
    except:
        pass
    url = settings.GEOSERVER_BASE_URL + "%s/%s/" % tuple(layer.typename.split(':'))
    url = url + "wms?request=getcapabilities&version=1.1.0"
    try:
        xml = urlopen(url).read()
    except Exception,ex:
        raise CheckFailed('error reading from url: %s , %s',url,ex)
    try:
        dom = fromstring(xml)
    except:
        raise CheckFailed('invalid xml:\n%s' % xml)