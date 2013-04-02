from django.conf import settings

from mapstory.models import *
from mapstory.util import lazy_context

import re

@lazy_context
def _sections():
    return list(Section.objects.order_by('order'))

@lazy_context
def _resources():
    return list(Resource.objects.order_by('order'))

_ua = re.compile('MSIE (\d+)\.')

def page(req):
    '''provide base template context'''
    # detect old browsers - probably should fix to use more robust framework
    # for now, IE7 causes lots of trouble
    old_browser = False
    agent = req.META.get('HTTP_USER_AGENT','')
    if agent:
        match = _ua.search(agent)
        if match:
            try:
                version = int(match.group(1))
                old_browser = version < 8
            except:
                pass
        if old_browser:
            # the user has understood
            if 'iunderstand' in req.COOKIES:
                old_browser = False
    
    #@todo better of using a template_tag
    page = {
        'sections' : _sections(),
        'resources' : _resources(),
        #@todo temp for design work
        'design_mode' : settings.DESIGN_MODE,
        # we could do this through debug but it's nicer to have finer grained control
        'enable_analytics' : settings.ENABLE_ANALYTICS,
        'old_browser' : old_browser
    }
    allow_signup = getattr(settings, 'ACCOUNT_OPEN_SIGNUP', False)
    enable_social_login = getattr(settings, 'ENABLE_SOCIAL_LOGIN', False)
    return {'page':page, 'cache_time':60, 'ACCOUNT_OPEN_SIGNUP': allow_signup,
            'ENABLE_SOCIAL_LOGIN': enable_social_login}
