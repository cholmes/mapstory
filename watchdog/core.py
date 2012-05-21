from django.conf import settings

import tempfile
import logging
import time

_default_config = {
    'LOG_DIR' : tempfile.gettempdir()
}
_config = {}

logger = logging.getLogger('watchdog')
logger.setLevel(logging.INFO)
_file_handler = None

def check(func):
    return _check(func)

def check_many(func):
    def inner():
        many = func()
        for f in many:
            _check(f)()
    inner.__name__ = str(func.__name__)
    return inner

def _check(func):
    def inner():
        t = time.time()
        try:
            func()
            logger.info('Check "%s" passed. Elapsed %.3f', func.__name__, time.time() - t)
        except CheckFailed,cf:
            logger.warning('Check "%s" failed: \n%s', func.__name__, cf)
        except Exception, ex:
            logger.warning('Check "%s" failed: \n%s', func.__name__, ex)
            logger.exception('Exception')
    inner.__name__ = str(func.__name__)
    return inner

def run_watchdog_suites(*suites):
    '''run one or more watchdog suites'''
    
    try:
        _conf = getattr(settings, 'WATCHDOG')
    except AttributeError:
        print 'using default settings for watchdog, to override, add WATCHDOG spec to settings'
        _conf = _default_config
    
    _config.update(_conf)
    
    
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
        
    for s in suite_funcs:
        _run_suite(s)
        
def _run_suite(func):
    _file_handler = logging.FileHandler('%s/%s-watchdog.log' % (_config['LOG_DIR'],func.__module__))
    _file_handler.setLevel(logging.INFO)
    
    logger.handlers.append(_file_handler)
    try:
        parts = func()
        for p in parts:
            logger.info('running part %s', p.__name__)
            p()
    except:
        logger.exception('watchdog funtion error')
    finally:
        _file_handler.close()
        logger.handlers.remove(_file_handler)
    
class CheckFailed(Exception):
    pass