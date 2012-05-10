from django import template
from django.template import loader
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from geonode.maps.models import Map
from geonode.maps.models import Layer
from mapstory.models import Section
from mapstory.models import Favorite
from mapstory.models import PublishingStatus

import re

register = template.Library()

# @todo lots of duplication can be removed

@register.filter
def user_name(obj):
    if hasattr(obj,'owner'):
        obj = obj.owner
    if obj.first_name:
        name = '%s %s' % (obj.first_name,obj.last_name)
    else:
        name = obj.username
    return name

@register.simple_tag
def active_nav_tab(req, which):
    if which == 'sections':
        if req.path == '/' or req.path == '' or req.path.startswith('/mapstory/section'):
            return 'active_nav'
    if which == 'search' and req.path.find('search') >= 0:
        return 'active_nav'
    return ''

@register.simple_tag
def active_sub_nav(request, pattern):
    if pattern and re.match(pattern, request.path):
        return 'active_nav'
    return ''

@register.tag
def map_info_tile(parser, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
        obj_name = tokens.pop(0)
        template = "center"
        if tokens:
            template = tokens.pop()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return MapInfoTileNode(obj_name, template)

class MapInfoTileNode(template.Node):
    def __init__(self, obj_name, template):
        self.obj_name = obj_name
        self.template = template
    def render(self, context):
        obj = context[self.obj_name]
        position = self.template == 'left' and '_left' or ''
        template_name = "mapstory/_story_tile%s.html" % position
        when = hasattr(obj,'last_modified') and obj.last_modified or obj.date
        return loader.render_to_string(template_name,{'map':obj,'when':when})
    
@register.tag
def about_storyteller(parse, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
        obj_name = tokens.pop(0)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return AboutStoryTellerNode(obj_name)

class AboutStoryTellerNode(template.Node):
    def __init__(self, obj_name):
        self.obj_name = obj_name
    def render(self, context):
        obj = context[self.obj_name]
        template_name = "maps/_widget_about_storyteller.html"
        return loader.render_to_string(template_name,{'map':obj})
    
@register.tag
def topic_selection(parse, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
        obj_name = tokens.pop(0)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return TopicSelectionNode(obj_name)

class TopicSelectionNode(template.Node):
    def __init__(self, obj_name):
        self.obj_name = obj_name
    def render(self, context):
        obj = context[self.obj_name]
        template_name = "maps/_widget_topic_selection.html"
        return loader.render_to_string(template_name,{
            'topic_object': obj,
            'sections' : Section.objects.all(),
            'topic_object_type': isinstance(obj, Map) and 'map' or 'layer'
        })

@register.tag
def comments_section(parse, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
        obj_name = tokens.pop(0)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return CommentsSectionNode(obj_name)

class CommentsSectionNode(template.Node):
    def __init__(self, obj_name):
        self.obj_name = obj_name
    def render(self, context):
        obj = context[self.obj_name]
        template_name = "maps/_widget_comments.html"
        r = loader.render_to_string(template_name,RequestContext(context['request'],{
            'comment_object' : obj
        }))
        return r

@register.tag
def related_mapstories(parse, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
        obj_name = tokens.pop(0)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return RelatedStoriesNode(obj_name)

class RelatedStoriesNode(template.Node):
    def __init__(self, obj_name):
        self.obj_name = obj_name
    def render(self, context):
        obj = context[self.obj_name]
        if isinstance(obj, Section):
            topics = obj.topics.all()
        else:
            topics = list(obj.topic_set.all())
        result = ""
        template_name = "mapstory/_story_tile_left.html"
        
        # @todo gather from all topics and respective sections
        sections = topics and topics[0].section_set.all() or None
        if topics and sections:
            sec = sections[0]
            maps = sec.get_maps()
            if isinstance(obj, Map) and obj in maps:
                maps.remove(obj)
            result = "\n".join([
                loader.render_to_string(template_name,{"map": m}) for m in maps
            ])
        return result
    
@register.tag
def favorites(parse, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return FavoritesNode()

class FavoritesNode(template.Node):
    def render(self, context):
        template_name = "mapstory/_widget_favorites.html"
        user = context['user']
        ctx = {
            "favorites" : Favorite.objects.favorites_for_user(user),
            "in_progress" : Map.objects.filter(owner=user, publish__status='In Progress')
        }
        return loader.render_to_string(template_name,ctx)
    
@register.tag
def add_to_favorites(parse, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
        obj_name = tokens.pop(0)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return AddToFavoritesNode(obj_name)

class AddToFavoritesNode(template.Node):
    def __init__(self,obj_name):
        self.obj_name = obj_name
    def render(self, context):
        template = '<a class="add-to-favorites btn btn-mini" href="%s"><i class="icon-heart"></i>%s</a>'
        obj = context[self.obj_name]
        obj_name = isinstance(obj,Map) and "map" or "layer"
        url = "add_favorite_%s" % obj_name
        url = reverse(url, args=[obj.pk])
        text = "Add to Favorites"
        return template % (url,text)
    
@register.tag
def add_to_map(parse, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
        obj_name = tokens.pop(0)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return AddToMapNode(obj_name)

class AddToMapNode(template.Node):
    def __init__(self,obj_name):
        self.obj_name = obj_name
    def render(self, context):
        layer = context[self.obj_name]
        user = context['user']
        template_name = 'mapstory/_widget_add_to_map.html'
        return loader.render_to_string(template_name,{
            'maps' : PublishingStatus.objects.get_in_progress(user), # user.map_set.all()
            'layer' : layer
        })

@register.tag
def by_storyteller(parse, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
        obj_name = tokens.pop(0)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return ByStoryTellerNode(obj_name)

class ByStoryTellerNode(template.Node):
    def __init__(self,obj_name):
        self.obj_name = obj_name
    def render(self, context):
        obj = context[self.obj_name]
        if isinstance(obj, User):
            user = obj
        else:
            user = obj.owner
        template_name = "maps/_widget_by_storyteller.html"
        layers = user.layer_set.all()
        for e in settings.LAYER_EXCLUSIONS:
            layers = layers.exclude(name__regex=e)
        maps = set(PublishingStatus.objects.get_public(user))
        #@todo could make query more efficient/explicit to exclude map
        if obj in maps:
            maps.remove(obj)
        return loader.render_to_string(template_name,{
            'user':user,
            'maps':maps,
            'layers':layers
        })