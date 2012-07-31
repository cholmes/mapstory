from datetime import datetime
from datetime import timedelta
from django.conf import settings
from django.core import urlresolvers
from django.core.mail import EmailMessage
from mapstory.watchdog.handlers import MemoryHandler
from mapstory.watchdog.models import get_current_state
from mapstory.watchdog.models import format_datestring
from mapstory.watchdog.models import Run
import functools
import inspect
import logging
import mapstory.watchdog.suites
import os
import subprocess
import tempfile
import time
import urllib2

_default_config = {
    'LOG_DIR': tempfile.gettempdir(),
    'CONSOLE': True,
    'FROM': 'watchdog@example.com',
    'TO': ['rob@example.com'],
    'GEOSERVER_LOG': '/var/lib/tomcat6/logs/geoserver.log',
    'RESTART_COMMAND': ['/etc/init.d/tomcat6', 'restart'],
    'GEOSERVER_BASE_URL': settings.GEOSERVER_BASE_URL,
    'GEOSERVER_DATA_DIR': '/var/lib/geoserver/geonode-data',
    'DJANGO_URL': 'http://localhost:8000',
}
_config = {}

logger = logging.getLogger('watchdog')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

memory_log_handler = MemoryHandler()
memory_log_handler.setFormatter(formatter)
logger.handlers.append(memory_log_handler)

_file_handler = None

# collect messages to email
_error_messages = []

# log files to email
_log_files = []

# keep track of errors as they come in from check function
_errors = []


# swiped from http://wiki.python.org/moin/PythonDecoratorLibrary#Creating_Well-Behaved_Decorators_.2BAC8_.22Decorator_decorator.22
def decorator(func):
    ''' Allow to use decorator either with arguments or not. '''
    def isFuncArg(*args, **kw):
        return len(args) == 1 and len(kw) == 0 and (
            inspect.isfunction(args[0]) or isinstance(args[0], type))

    if isinstance(func, type):
        def class_wrapper(*args, **kw):
            if isFuncArg(*args, **kw):
                return func()(*args, **kw)  # create class before usage
            return func(*args, **kw)
        class_wrapper.__name__ = func.__name__
        class_wrapper.__module__ = func.__module__
        return class_wrapper

    @functools.wraps(func)
    def func_wrapper(*args, **kw):
        if isFuncArg(*args, **kw):
            return func(*args, **kw)

        def functor(userFunc):
            return func(userFunc, *args, **kw)

        return functor

    return func_wrapper


def subcheck(func, name, *args, **kw):
    '''Create a subcheck function. When using `check_many`, return a sequence
    of `subcheck` functions'''
    # for now, just a wrapper around partial that assigns a check provided name
    fn = functools.partial(func, *args, **kw)
    fn.__subcheck__ = name
    return fn


@decorator
def check(func, **kw):
    '''Decorator to enable a check'''
    return _check(func, **kw)


@decorator
def check_many(func, **kw):
    '''Decorator to enable running multiple checks. The function must return
    a sequence of `subcheck` functions.'''
    def outer():
        many = func()
        for f in many:
            f.__name__ = '%s_%s' % (func.__name__, f.__subcheck__)
            _run_check(f, **kw)
    outer.__name__ = str(func.__name__)
    return outer


def _check(func, **kw):
    def inner():
        _run_check(func, **kw)
    inner.__name__ = str(func.__name__)
    return inner


def _valid_args(**kw):
    _kw_list = ['restart_on_error', 'email_on_error']
    for k in kw:
        if kw not in _kw_list:
            raise Exception('Keyword %s is not valid' % k)


def _run_check(func, *args, **kw):
    t = time.time()
    ex = None
    try:
        func()
        logger.info('Check "%s" passed. Elapsed %.3f', func.__name__, time.time() - t)
    except CheckFailed, ex:
        logger.warning('Check "%s" failed:\n%s', func.__name__, ex)
        _errors.append(ex)
    except Exception, ex:
        logger.warning('Check "%s" failed:\n%s', func.__name__, ex)
        logger.exception('Exception: %s -> %s' % (type(ex).__name__, ex))
        _errors.append(ex)
        if isinstance(ex, RestartRequired):
            raise ex
    if ex and 'restart_on_error' in kw:
        raise RestartRequired(ex)
    if ex and 'email_on_error' in kw:
        error_message(ex)


def set_config():
    if not _config:
        try:
            _conf = getattr(settings, 'WATCHDOG')
        except AttributeError:
            print 'using default settings for watchdog, to override, add WATCHDOG spec to settings'
            _conf = _default_config
        _config.update(_conf)


def _run_watchdog_suites(*suites):
    '''run one or more watchdog suites'''

    set_config()

    if _config['CONSOLE']:
        root = logging.getLogger("")
        if not any([isinstance(h, logging.StreamHandler) for h in root.handlers]):
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            root.handlers.append(console)

    # resulve suite module
    suite_funcs = []
    for s in suites:
        module_name = 'mapstory.watchdog.suites.%s' % s
        try:
            module = __import__(module_name, fromlist=['*'], level=0)
        except ImportError:
            logger.exception('error importing')
            raise Exception('no suite found for: %s' % s)
        try:
            suite_funcs.append(getattr(module, 'suite'))
        except AttributeError:
            raise Exception('suite "%s" has no suite function' % module_name)

    restart = False
    try:
        _run_suites(suite_funcs)
    except RestartRequired, re:
        restart = True

    # no restart in loop
    if restart:
        error_message('A restart was required: %s' % re)
        if _restart():
            logger.info('Geoserver restart successful, rerunning suites')
            try:
                _run_suites(suite_funcs, after_restart=True)
            except RestartRequired, re:
                error_message('Restarted geoserver, but check did not recover: %s' % re)
        else:
            error_message('Failure Restarting Geoserver')

    # send out any error messages immediately
    _send_error_mails()

    # keep track of state from runs in database

    current_log = memory_log_handler.contents()
    is_error = bool(_errors)
    if is_error:
        separator = '\n\n%s\n\n' % ('=' * 80)
        errors = separator.join([str(error) for error in _errors])
    else:
        errors = None

    current_state = get_current_state()
    current_state.is_error = is_error
    current_state.save()

    run = Run(suites='\n'.join(suites),
              log=current_log,
              is_error=is_error,
              errors=errors)
    run.save()


def error_message(msg):
    """these messages will get emailed out immediately after the run"""
    logger.error(msg)
    _error_messages.append(msg)


def _run_suites(suite_funcs, after_restart=False):
    for s in suite_funcs:
        _run_suite(s, after_restart)


def verify_geoserver_running(attempt=1):
    if attempt > 5:
        return False
    try:
        logger.info('Attempt %d at checking if geoserver is running' % attempt)
        result = urllib2.urlopen(_config['GEOSERVER_BASE_URL'])
        if result.getcode() != 200:
            time.sleep(10)
            return verify_geoserver_running(attempt=attempt + 1)
    except Exception:
        time.sleep(10)
        return verify_geoserver_running(attempt=attempt + 1)
    return True


def _restart():
    cmd = _config['RESTART_COMMAND']
    logger.warn('Restarting using command: %s'
                % ' '.join(cmd))

    # save restarting state in database
    state = get_current_state()
    state.geoserver_restarting = True
    state.save()

    return_code = subprocess.call(cmd)
    if return_code != 0:
        logger.error('Failure executing restart command: %s'
                     % ' '.join(cmd))
        logger.error('Received error response code: %s' % return_code)
        return False

    # instead of trying to detect whether tomcat shut down correctly,
    # sleep for a few seconds
    time.sleep(10)

    if verify_geoserver_running(attempt=1):
        state.geoserver_restarting = False
        state.save()
        return True
    return False


def _format_watchdog_subject(s):
    return '[Watchdog] %s' % s


def _send_with_attachments(subject, body):
    msg = EmailMessage(
        subject,
        body,
        _config['FROM'],
        _config['TO'],
        )
    for filename in _log_files:
        if os.path.exists(filename):
            msg.attach_file(filename)
        else:
            logger.warn('Log file to attach not found: %s' % filename)
    msg.send()


def _send_error_mails():
    if _error_messages:
        for msg in _error_messages:
            _send_with_attachments(
                _format_watchdog_subject(msg),
                memory_log_handler.contents(),
                )


def _run_suite(func, after_restart):
    log_file = ('%s/%s-watchdog%s.log' %
                (_config['LOG_DIR'], func.__module__,
                 after_restart and '-after-restart' or ''))
    _log_files.append(log_file)

    _file_handler = logging.FileHandler(log_file)
    _file_handler.setLevel(logging.INFO)
    _file_handler.setFormatter(formatter)
    logger.handlers.append(_file_handler)

    try:
        parts = func()
        for p in parts:
            logger.info('running part %s', p.__name__)
            p()
    except Exception, ex:
        if isinstance(ex, RestartRequired):
            raise ex
        logger.exception('watchdog function error')
    finally:
        _file_handler.close()
        logger.handlers.remove(_file_handler)


def list_suites():
    suites = []
    watchdog_import_path = mapstory.watchdog.suites.__file__
    watchdog_path = os.path.dirname(watchdog_import_path)
    for f in os.listdir(watchdog_path):
        fullpath = os.path.join(watchdog_path, f)
        if fullpath.endswith('.py'):
            with open(fullpath) as fileobj:
                if 'def suite():' in fileobj.read():
                    basename = os.path.splitext(f)[0]
                    if basename != 'core':
                        suites.append(basename)
    print '\n'.join(sorted(suites))


def clean_runs(ndays):
    now = datetime.now()
    delta = timedelta(days=ndays)
    cutoff = now - delta
    old_runs = Run.objects.filter(time__lte=cutoff, is_error=False)
    for run in old_runs:
        run.delete()


def summarize(start_time, end_time):
    set_config()
    base_url = _config['DJANGO_URL']
    runs = Run.objects.filter(time__range=(start_time, end_time))
    total = 0
    success = 0
    failure = 0
    failures = []
    for run in runs:
        total += 1
        if run.is_error:
            failure += 1
            failures.append(run)
        else:
            success += 1
    print "Watchdog runs between %s and %s" % (start_time.strftime('%m/%d'),
                                               end_time.strftime('%m/%d'))
    print '=' * 37
    print "%s total\n%s succeeded\n%s failed" % (total, success, failure)
    if failures:
        def admin_url(run_id):
            path = urlresolvers.reverse('admin:watchdog_run_change',
                                        args=(run_id,))
            return base_url + path
        print
        print 'Failures'
        print '========'
        print '\n'.join([
            '%s @ %s' % (admin_url(run.id), format_datestring(run.time))
            for run in failures])


class CheckFailed(Exception):
    pass


class RestartRequired(Exception):
    pass
