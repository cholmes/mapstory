from django.contrib.markup.templatetags import markup
from django.core.cache import cache
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

import hotshot
import os
import time
import threading

try:
    PROFILE_LOG_BASE = settings.PROFILE_LOG_BASE
except:
    PROFILE_LOG_BASE = "/tmp"


current_request = threading.local()

def user():
    req = getattr(current_request, 'request', None)
    return req.user if req else None

class GlobalRequestMiddleware(object):
    def process_request(self, request):
        current_request.request = request
    

def render_manual(*path):
    paths = [settings.PROJECT_ROOT,'manual']
    paths.extend(path)
    cache_key = 'mapstory_manual_%s' % ('_'.join(paths))
    html = cache.get(cache_key)
    if html is None or settings.DEBUG:
        html = markup(os.path.join(*paths))
        cache.set(cache_key, html, 60000)
    return html


def markup(path):
    '''this is borrowed from core django but adds stuff to allow inclusion
    of other fragments
    '''
    with open(path) as fp: value = fp.read()
    try:
        from docutils.core import publish_parts
    except ImportError:
        if settings.DEBUG:
            raise Exception("The Python docutils library isn't installed.")
    else:
        overrides = {
            'file_insertion_enabled' : True
        }
        parts = publish_parts(source=smart_str(value),
                              source_path=path,
                              writer_name="html4css1", 
                              settings_overrides=overrides)
        return mark_safe(force_unicode(parts["fragment"]))



def profile(log_file=None):
    """Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the 
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof', 
    where the time stamp is in UTC. This makes it easy to run and compare 
    multiple trials.     
    """

    if not os.path.isabs(log_file):
        log_file = os.path.join(PROFILE_LOG_BASE, log_file)

    def _outer(f):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.
            (base, ext) = os.path.splitext(log_file or f.__name__)
            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            prof = hotshot.Profile(final_log_file)
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
            return ret

        return _inner
    return _outer

def lazy_context(f):
    '''build a factory for lazy context objects'''
    def value(s):
        if s._value is None:
            s._value = f()
        return s._value
    lazy_type = type('lazy_%s' % f.__name__,(object,), dict(
        value = value,
        _value = None
    ))
    def _inner(*args, **kw):
        return lazy_type()

    return _inner
    