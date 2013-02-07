from django.conf import settings

import httplib2
from urlparse import urlparse
from xml.etree.ElementTree import XML
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import tostring

import logging

logger = logging.getLogger(__name__)


def _el(n, t=None, **atts):
    '''build an element with t for text and atts for atts'''
    el = Element(n)
    el.text = str(t)
    for k,v in atts.items():
        el.set(k, str(v))
    return el


def _gwc_client():
    http = httplib2.Http()
    http.add_credentials(*settings.GEOSERVER_CREDENTIALS)
    netloc = urlparse(settings.GEOSERVER_BASE_URL).netloc
    http.authorizations.append(
        httplib2.BasicAuthentication(
            settings.GEOSERVER_CREDENTIALS,
                netloc,
                settings.GEOSERVER_BASE_URL,
                {},
                None,
                None,
                http
            )
        )
    return http


def _enable_wms_caching(layer, cache_secs, disable=False):
    '''This should go into gsconfig'''
    layer.resource.fetch()
    dom = layer.resource.dom
    metadata = dom.find('metadata')
    if metadata is None:
        metadata = _el('metadata')
        dom.append(metadata)
    def set_entry(k, v):
        entries = metadata.findall("entry")
        entries = [ e for e in entries if e.attrib.get('key', None) == k]
        entry = entries[0] if entries else None
        if v:
            if entry is None:
                entry = _el('entry', v, key=k)
                metadata.append(entry)
            else:
                entry.text = str(v)
        elif entry is not None:
            metadata.remove(entry)
    set_entry('cacheAgeMax', cache_secs)
    set_entry('cachingEnabled', 'false' if disable or cache_secs is 0 else 'true')
    headers, resp = layer.resource.catalog.http.request(
        layer.resource.href, 'PUT', tostring(dom), {'content-type' : 'text/xml'})
    if headers.status != 200:
        raise Exception('error enabling wms caching: %s' % resp)


def configure_layer(layer, cache_secs):
    '''Configure a GWC layer with time parameter and WMS expires
    The GWC layer must exist or this will fail.
    '''
    typename = layer.typename
    try:
        _configure_layer(typename)
    except:
        logger.exception('Error configuring GWC for %s',typename)
    try:
        _enable_wms_caching(layer, cache_secs)
    except:
        logger.exception('Error configuring WMS caching for %s',typename)


def _list_gwc_layers(client=None):
    '''get a dict of layer->href'''
    if not client:
        client = _gwc_client()

    url = settings.GEOSERVER_BASE_URL + 'gwc/rest/layers/'

    headers, response = client.request(url, 'GET')
    if headers.status != 200: raise Exception('listing failed - %s, %s' %
                                              (headers,response))

    # try to resolve layer if already configured
    dom = XML(response)
    layers = {}
    for layer in dom.getchildren():
        els = layer.getchildren()
        layers[els[0].text] = els[1].get('href')
    return layers


def _get_config(client, url):
    headers, response = client.request(url, 'GET')
    if headers.status == 404:
        return None
    elif headers.status != 200:
        raise Exception('error retreiving config for %s' % url)
    return XML(response)


def _configure_layer(typename):
    '''Enable gwc time caching for a layer. Needs to support checking for layers
    that do not have a tile layer configured.

    See: create_layer_configs
    '''

    client = _gwc_client()

    # searching through the list is not worth it, we know the URL and it will
    # fail otherwise
    url = settings.GEOSERVER_BASE_URL + 'gwc/rest/layers/%s.xml' % typename

    dom = _get_config(client, url)
    if dom is None:
        raise Exception('%s not found in gwc config' % typename)

    _add_time_parameter(dom)
    
    headers, response = client.request(url, 'POST', tostring(dom))
    if headers.status < 200 or headers.status >= 300:
        raise Exception('expected success, got %s - %s' 
                        % (headers.status, response))


def _add_time_parameter(dom):
    filters = dom.find('parameterFilters')
    # if already configured, done
    if filters is not None:
        if filters.find('regexParameterFilter') is not None:
            return
    if filters is None:
        filters = _el('parameterFilters')
        dom.append(filters)
    time_filter = _el('regexParameterFilter')
    time_filter.append(_el('key', 'TIME'))
    time_filter.append(_el('defaultValue'))
    time_filter.append(_el('regex', '.*'))
    filters.append(time_filter)


def create_layer_configs(layers):
    '''Ensure a GWC config exists for all layers. This is really only for fixing'''
    client = _gwc_client()
    configs = _list_gwc_layers(client)
    template = _get_config(client, configs.values()[0])
    # remove the layerid or the template will not work
    template.remove(template.find('id'))
    _add_time_parameter(template)
    for l in layers:
        if l.typename in configs:
            continue
        name = template.find('name')
        name.text = l.typename
        logging.info('creating config for %s', l.typename)
        url = settings.GEOSERVER_BASE_URL + 'gwc/rest/layers/' + l.typename + '.xml'
        headers, resp = client.request(url, 'PUT', tostring(template))
        if headers.status != 200:
            logging.warning('failure %s %s', headers, resp)


