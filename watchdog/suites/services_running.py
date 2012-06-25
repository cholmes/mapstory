# ensure that the applications are responding to a basic ping

from mapstory.watchdog.core import CheckFailed
from mapstory.watchdog.core import _config
from mapstory.watchdog.core import check
import urllib2


def suite():
    return (
        django_up,
        geoserver_up,
        )


def ok_response_from(url, timeout=30):
    result = urllib2.urlopen(url, timeout=timeout)
    if result.getcode() != 200:
        raise CheckFailed('Invalid response from %s' % url)


@check(email_on_error=True)
def django_up():
    ok_response_from(_config['DJANGO_URL'])


@check(email_on_error=True)
def geoserver_up():
    ok_response_from(_config['GEOSERVER_BASE_URL'])
