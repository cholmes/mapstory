from django.conf import settings
from geonode.maps.models import Layer
from urllib import urlopen
from mapstory.watchdog.core import _config
from mapstory.watchdog.core import check
from mapstory.watchdog.core import check_many
from mapstory.watchdog.core import subcheck
from mapstory.watchdog.core import CheckFailed
from mapstory.watchdog.core import RestartRequired
from mapstory.watchdog.models import get_logfile_model
from mapstory.watchdog.logs import checksum
from mapstory.watchdog.logs import read_next_sections
from xml.etree.ElementTree import fromstring
import os


def suite():
    return (
        get_capabilities,
        get_layer_capabilities,
        check_geoserver_log,
    )


@check
def get_capabilities():
    Layer.objects.get_wms()


@check_many
def get_layer_capabilities():
    return [subcheck(_check_layer_capabilities, l.typename, l)
            for l in Layer.objects.all().iterator()]


@check_many
def get_layer_has_latlon_bbox():
    return [subcheck(_check_layer, l.typename, l)
            for l in Layer.objects.all().iterator()]


@check_many
def check_geoserver_log():
    logpath = _config['GEOSERVER_LOG']
    if not os.path.isfile(logpath):
        raise CheckFailed('Invalid logpath: %s' % logpath)
    logfile_model = get_logfile_model(logpath)
    with open(logpath) as f:
        result = read_next_sections(f, logfile_model)
        sections = result['sections']
        logfile_model.offset_start = start = result['offset_start']
        logfile_model.offset_end = end = result['offset_end']
        logfile_model.checksum = checksum(sections, start, end)
        logfile_model.save()
    return [subcheck(fn, name, sections)
            for fn, name in [(_out_of_memory, 'Out of Memory')]]


def _out_of_memory(sections):
    for section in sections:
        for line in section:
            if 'java.lang.OutOfMemoryError: PermGen space' in line:
                raise RestartRequired('Out Of Memory')


def _check_layer():
    pass


def _check_layer_latlon_bbox(layer):
    if layer.resource.latlon_bbox is None:
        raise CheckFailed('missing bbox')


def _check_layer_capabilities(layer):
    try:
        layer.metadata()
        return
    except:
        pass
    url = settings.GEOSERVER_BASE_URL + "%s/%s/" % tuple(layer.typename.split(':'))
    url = url + "wms?request=getcapabilities&version=1.1.0"
    try:
        xml = urlopen(url).read()
    except Exception, ex:
        raise CheckFailed('error reading from url: %s, %s', url, ex)
    try:
        fromstring(xml)
    except:
        raise CheckFailed('invalid xml:\n%s' % xml)
