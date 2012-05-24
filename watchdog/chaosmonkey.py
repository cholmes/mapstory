from webob.exc import HTTPInternalServerError
import logging
import time

logger = logging.getLogger('mapstory.watchdog.watchmonkey')
logger.setLevel(logging.INFO)
logger.handlers.append(logging.StreamHandler())


def filter_factory(global_conf, **local_conf):
    def filter_app(app):
        return generate_chaosmonkey_app(local_conf, app)
    return filter_app


def error_response(app):
    def handler(environ, start_response, msg=None):
        if msg is None:
            msg = u'ChaosMonkey Error'
        logger.info('generating error')
        resp = HTTPInternalServerError(body=msg)
        return resp(environ, start_response)
    return handler


def timeout_response(app):
    default_length = 5

    def handler(environ, start_response, length=None):
        try:
            timeout = int(length)
        except ValueError:
            timeout = default_length
        except TypeError:
            timeout = default_length

        logger.info('sleeping for: %s seconds' % timeout)

        time.sleep(timeout)
        return app(environ, start_response)

    return handler


def log_response(app):
    # XXX just placeholders for now
    # will most likely want to read this in from a file instead
    log_text = {
        'out-of-memory': 'java.lang.OutOfMemory\n',
        'npe': 'NullPointerException\n',
        }
    default_exception = 'npe'
    default_file = 'foo.log'

    def handler(environ, start_response, exception=None, file=None):
        if exception is None:
            exception = default_exception
        if file is None:
            file = default_file
        msg = log_text.get(exception)
        if msg is None:
            logger.warn('Unknown exception type: %s' % exception)
        else:
            logger.info('Adding log message to: %s' % file)
            with open(file, 'a') as f:
                f.write(msg)

        return app(environ, start_response)

    return handler


def generate_chaosmonkey_app(local_conf, app):
    # read all parameters from ini file
    params = {}
    for k, v in local_conf.items():
        # a '.' means it is a configurable parameter we should be interested in here,
        # and not a path
        if '.' in k:
            paramtype, option, for_path = k.split('.')
            params.setdefault(paramtype, {}).setdefault(for_path, {}).setdefault(option, v)

    # generate the different kinds of monkey middleware with the appropriate params
    fn_map = dict(
        error=error_response(app),
        timeout=timeout_response(app),
        log=log_response(app),
        )

    # dispatch to the appropriate handler based on the path
    def chaosmonkey(environ, start_response):
        path = environ['PATH_INFO']
        monkey_with_fn = local_conf.get(path)
        if monkey_with_fn is not None:
            logger.info('monkeying with path: ' + path)
            fn = fn_map[monkey_with_fn]
            kwargs = params.get(monkey_with_fn, {}).get(path, {})
            return fn(environ, start_response, **kwargs)
        else:
            logger.debug('passing through: ' + path)
            return app(environ, start_response)

    return chaosmonkey
