from django.conf import settings

from mapstory.models import *

def page(req):
    page = {
        #@todo use filter
        'sections' : Section.objects.all(),
        #@todo temp for design work
        'design_mode' : settings.DESIGN_MODE
    }
    return {'page':page}