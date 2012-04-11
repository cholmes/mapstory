from django.conf import settings

from mapstory.models import *
from mapstory.util import lazy_context

@lazy_context
def _sections():
    return list(Section.objects.order_by('order'))

@lazy_context
def _resources():
    return list(Resource.objects.order_by('order'))

def page(req):
    '''provide base template context'''
    #@todo better of using a template_tag
    page = {
        'sections' : _sections(),
        'resources' : _resources(),
        #@todo temp for design work
        'design_mode' : settings.DESIGN_MODE
    }
    return {'page':page,'cache_time':60}