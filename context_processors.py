from django.conf import settings

from mapstory.models import *
from mapstory.util import lazy_context

@lazy_context
def _sections():
    return list(Section.objects.order_by('order'))

def page(req):
    page = {
        #@todo use filter
        'sections' : _sections(),
        #@todo temp for design work
        'design_mode' : settings.DESIGN_MODE
    }
    return {'page':page}