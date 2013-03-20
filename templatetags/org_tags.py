from django import template
from django.template import loader
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags import staticfiles
from django.conf import settings
from mapstory.models import Org

import re

register = template.Library()

@register.simple_tag(takes_context=True)
def edit_widget(context, part_name):
    _widget_button = "<a href='#%s' class='edit-btn btn btn-small'>%s</a>"
    if not context['can_edit']: return ""
    return _widget_button % (part_name,'Edit')
        