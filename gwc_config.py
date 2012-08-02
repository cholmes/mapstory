from django.conf import settings

import httplib2
from urlparse import urlparse
from xml.etree.ElementTree import XML
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import tostring

import logging

logger = logging.getLogger(__name__)

def configure_layer(typename):
    try:
        _configure_layer(typename)
    except:
        logger.exception('Error configuring GWC for %s',typename)

def _configure_layer(typename):
    
    url = settings.GEOSERVER_BASE_URL + 'gwc/rest/layers/'
          
    http = httplib2.Http()
    http.add_credentials(*settings.GEOSERVER_CREDENTIALS)
    netloc = urlparse(url).netloc
    http.authorizations.append(
        httplib2.BasicAuthentication(
            settings.GEOSERVER_CREDENTIALS, 
                netloc,
                url,
                {},
                None,
                None, 
                http
            )
        )
    
    headers, response = http.request(url, 'GET')
    if headers.status != 200: raise Exception('listing failed - %s, %s' % 
                                              (headers,response))
                                              
    url = None
    dom = XML(response)
    for layer in dom.getchildren():
        els = layer.getchildren()
        if els[0].text == typename:
            url = els[1].get('href')
            break
    if url is None: raise Exception('could not locate %s in listing' % typename)
    
    headers, response = http.request(url, 'GET')
    if headers.status != 200: raise Exception('layer request failed - %s, %s' % 
                                              (headers,response))
    
    def el(n, t=None):
        el = Element(n)
        el.text = t
        return el
    dom = XML(response)
    filters = dom.find('parameterFilters')
    time_filter = el('regexParameterFilter')
    time_filter.append(el('key', 'TIME'))
    time_filter.append(el('defaultValue'))
    time_filter.append(el('regex', '.*'))
    filters.append(time_filter)
    
    headers, response = http.request(url, 'POST', tostring(dom))
    if headers.status < 200 or headers.status >= 300:
        raise Exception('expected success, got %s - %s' 
                        % (headers.status, response))