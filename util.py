import hotshot
import os
import time
import settings

try:
    PROFILE_LOG_BASE = settings.PROFILE_LOG_BASE
except:
    PROFILE_LOG_BASE = "/tmp"


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
            print 'loading value'
            s._value = f()
        return s._value
    lazy_type = type('lazy_%s' % f.__name__,(object,), dict(
        value = value,
        _value = None
    ))
    def _inner(*args, **kw):
        return lazy_type()

    return _inner
    