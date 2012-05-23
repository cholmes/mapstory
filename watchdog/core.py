from django.conf import settings

import tempfile
import logging
import time
import functools
import inspect

_default_config = {
    'LOG_DIR' : tempfile.gettempdir()
}
_config = {}

logger = logging.getLogger('watchdog')
logger.setLevel(logging.INFO)
_file_handler = None

# collect messages to email
_messages = []

# log files to email
_log_files = []

# swiped from http://wiki.python.org/moin/PythonDecoratorLibrary#Creating_Well-Behaved_Decorators_.2BAC8_.22Decorator_decorator.22
def decorator(func):
    ''' Allow to use decorator either with arguments or not. '''
    def isFuncArg(*args, **kw):
        return len(args) == 1 and len(kw) == 0 and (
            inspect.isfunction(args[0]) or isinstance(args[0], type))

    if isinstance(func, type):
        def class_wrapper(*args, **kw):
            if isFuncArg(*args, **kw):
                return func()(*args, **kw) # create class before usage
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

@decorator
def subcheck(func,name,**kw):
    '''Create a subcheck function. When using `check_many`, return a sequence
    of `subcheck` functions'''
    # for now, just a wrapper around partial that assigns a check provided name
    func = functools.partial(func,**kw)
    func.__subcheck__ = name
    return func

@decorator
def check(func,**kw):
    '''Decorator to enable a check'''
    return _check(func,**kw)

@decorator
def check_many(func,**kw):
    '''Decorator to enable running multiple checks. The function must return
    a sequence of `subcheck` functions.'''
    def outer(func):
        many = func()
        for f in many:
            f.__name__ = '%s_%s' % (func.__name__, f.__subcheck__)
            _run_check(f,**kw)
    inner.__name__ = str(func.__name__)
    return outer

def _check(func,**kw):
    def inner():
        _run_check(func,**kw)
    inner.__name__ = str(func.__name__)
    return inner

def _valid_args(**kw):
    _kw_list = ['restart_on_error']
    for k in kw:
        if kw not in _kw_list:
            raise Exception('Keyword %s is not valid' % k)

def _run_check(func,*args,**kw):
    t = time.time()
    ex = None
    try:
        func()
        logger.info('Check "%s" passed. Elapsed %.3f', func.__name__, time.time() - t)
    except CheckFailed,ex:
        logger.warning('Check "%s" failed: \n%s', func.__name__, ex)
    except Exception, ex:
        logger.warning('Check "%s" failed: \n%s', func.__name__, ex)
        logger.exception('Exception')
    if ex and 'restart_on_error' in kw:
        raise RestartRequired()
        

def _run_watchdog_suites(*suites):
    '''run one or more watchdog suites'''
    
    try:
        _conf = getattr(settings, 'WATCHDOG')
    except AttributeError:
        print 'using default settings for watchdog, to override, add WATCHDOG spec to settings'
        _conf = _default_config
    
    _config.update(_conf)
    
    # resulve suite module
    suite_funcs = []
    for s in suites:
        module_name = 'watchdog.%s' % s
        try:
            module = __import__(module_name, fromlist=['*'])
        except ImportError:
            logger.exception('error importing')
            raise Exception('no suite found for: %s' % s)
        try:
            suite_funcs.append(getattr(module,'suite'))
        except AttributeError:
            raise Exception('suite "%s" has no suite function' % module_name)
        
    restart = False
    try:
        _run_suites(suite_funcs)
    except RestartRequired,re:
        restart = True

    # no restart in loop
    if restart:
        _message('A restart was required: %s' % re)
        _restart()
        _run_suites(suite_funcs)
        
def _message(msg):
    logger.info(msg)
    _messages.append(msg)
        
def _run_suites(suite_funcs):
    for s in suite_funcs:
        _run_suite(s)
        
    
def _restart():
    # use something defined in settings, like:
    # tomcat_restart = 'service tomcat6 restart'
    
    # if restart fails - send email immediately
    todo
    
def _send_mail():
    todo
        
def _run_suite(func):
    log_file = '%s/%s-watchdog.log' % (_config['LOG_DIR'],func.__module__)
    _log_files.append(log_file)
    _file_handler = logging.FileHandler(log_file)
    _file_handler.setLevel(logging.INFO)
    
    logger.handlers.append(_file_handler)
    try:
        parts = func()
        for p in parts:
            logger.info('running part %s', p.__name__)
            p()
    except Exception,ex:
        if isinstance(ex,RestartRequired):
            raise ex
        logger.exception('watchdog funtion error')
    finally:
        _file_handler.close()
        logger.handlers.remove(_file_handler)
    
class CheckFailed(Exception):
    pass

class RestartRequired(Exception):
    pass
