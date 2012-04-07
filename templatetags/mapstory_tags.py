from django import template
from django.template import loader
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from geonode.maps.models import Map
from mapstory.models import Section
from mapstory.models import Favorite

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
        return loader.render_to_string(template_name,{'map':obj})
    
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
        if topics:
            sec = topics[0].section_set.all()[0]
            maps = sec.get_maps()
            if isinstance(obj, Map):
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
            "in_progress" : Favorite.objects.inprogress_for_user(user)
        }
        return loader.render_to_string(template_name,ctx)

@register.tag
def add_to_inprogress(parse, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
        obj_name = tokens.pop(0)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return AddToFavoritesNode(obj_name)

    
@register.tag
def add_to_favorites(parse, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
        obj_name = tokens.pop(0)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return AddToFavoritesNode(obj_name,True)

class AddToFavoritesNode(template.Node):
    def __init__(self,obj_name,in_progress=False):
        self.obj_name = obj_name
        self.in_progress = in_progress
    def render(self, context):
        template = '<a class="add-to-favorites btn btn-mini" href="%s"><i class="icon-heart"></i>%s</a>'
        obj = context[self.obj_name]
        obj_name = isinstance(obj,Map) and "map" or "layer"
        url = self.in_progress and "add_inprogress_%s" or "add_favorite_%s"
        url = url % obj_name
        url = reverse(url, args=[obj.pk])
        text = self.in_progress and "Add to InProgress" or "Add to Favorites"
        return template % (url,text)

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
        return loader.render_to_string(template_name,{'user':user})