from django import template
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Page
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags import staticfiles
from django.conf import settings
from geonode.maps.models import Map
from geonode.maps.models import Layer
from geonode.maps.models import ALL_LANGUAGES
from mapstory.models import Section
from mapstory.models import Favorite
from mapstory.models import PublishingStatus
from mapstory.models import PUBLISHING_STATUS_PRIVATE
from mapstory.models import PUBLISHING_STATUS_LINK
from mapstory.models import PUBLISHING_STATUS_PUBLIC
from mapstory.models import get_view_cnt_for
from mapstory.util import render_manual
from mapstory.views import _by_storyteller_pager
from mapstory.views import _related_stories_pager
from dialogos.templatetags import dialogos_tags

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

@register.simple_tag
def map_view_hitcount_tracker(req, obj):
    #obj may be an empty string as the newmap view also calls this but
    #with no map object
    if req.session.session_key is None:
        req.session['__created'] = True
        req.session.save()
    if obj and req.user is not obj.owner:
        return loader.render_to_string("maps/_widget_hitcount.html",{'obj': obj})
   
    
@register.simple_tag
def map_view_hitcount(obj):
    hits = get_view_cnt_for(obj)
    return "<span class='viewcnt'><i>%s</i> Views</span>" % _group(hits)

def _group(number):
    '''this could be replaced by '{:,}'.format but this is 2.6 compatible'''
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))


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
def publish_status(parse, token):
    try:
        tokens = token.split_contents()
        tag_name = tokens.pop(0)
        obj_name = tokens.pop(0)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return PublishStatusNode(obj_name)

class PublishStatusNode(template.Node):
    def __init__(self, obj_name):
        self.obj_name = obj_name
        options = [
            (PUBLISHING_STATUS_PRIVATE,"Only visible to me"),
            (PUBLISHING_STATUS_LINK,"Anyone with a link can view"),
            (PUBLISHING_STATUS_PUBLIC,"Anyone can search for and view"),
        ]
        self.options = [ dict(key=o[0],value=o[1]) for o in options ]
    def render(self, context):
        obj = context[self.obj_name]
        template_name = "maps/_widget_publish_status.html"
        current_status = [ o['value'] for o in self.options if o['key'] == obj.publish.status ][0]
        return loader.render_to_string(template_name,{
            'publish_object': obj,
            'publish_options' : self.options,
            'current_status' : current_status,
            'publish_object_type': isinstance(obj, Map) and 'map' or 'layer'
        })
    
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
    return CommentsSectionNode.handle_token(parse, token)

class CommentsSectionNode(dialogos_tags.ThreadedCommentsNode):
    template_name = 'maps/_widget_comments.html'


@register.simple_tag
def related_mapstories(map_obj):
    map_obj, pager = _related_stories_pager(map_obj=map_obj)
    ctx = {'map': map_obj,
           'pager': Page([], 0, pager)}
    return loader.render_to_string("maps/_widget_related_mapstories.html", ctx)


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
        maps = PublishingStatus.objects.get_in_progress(user,Map)
        layers = PublishingStatus.objects.get_in_progress(user,Layer)
        ctx = {
            "favorites" : Favorite.objects.favorites_for_user(user),
            "in_progress_maps" : maps,
            "in_progress_layers" : layers
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
            'maps' : PublishingStatus.objects.get_in_progress(user,Map), # user.map_set.all()
            'layer' : layer
        })

@register.simple_tag
def by_storyteller(obj):
    if isinstance(obj, User):
        user = obj
    else:
        user = obj.owner
    template_name = "maps/_widget_by_storyteller.html"
    maps_page = Page([], 0, _by_storyteller_pager(None, user, 'maps'))
    layers_page = Page([], 0, _by_storyteller_pager(None, user, 'layers'))
    return loader.render_to_string(template_name,{
        'user':user,
        'maps_pager': maps_page,
        'layers_pager': layers_page
    })
        
_link_template = "<a href='%s'>%s</a>"
_pt_link_template = "%s (%s)"
absolutize = lambda u: u if u.startswith("http:") else settings.SITEURL[:-1] + u
def _activity_link(subject, plain_text=False):
    object_name = subject.__class__._meta.object_name
    if object_name == 'Layer':
        parts = absolutize(subject.get_absolute_url()), "the StoryLayer '%s'" % subject.title
    elif object_name == 'Map':
        parts = absolutize(subject.get_absolute_url()), "the MapStory '%s'" % subject.title
    else:
        return subject
    return (_pt_link_template if plain_text else _link_template) % parts

@register.simple_tag
def activity_item(action, show_actor_link=True, plain_text=False):
    link_tmpl = _pt_link_template if plain_text else _link_template
    username = action.actor.get_full_name() or action.actor.username
    if show_actor_link:
        username = link_tmpl % (absolutize(action.actor.get_absolute_url()), username)
    subject = action.action_object
    object_name = subject.__class__._meta.object_name
    verb = action.verb
    if object_name == 'Comment':
        commented_obj = subject.content_object
        if commented_obj is None:
            # the map/layer the comment was made on is gone now, avoid junk in feed
            # @todo longer term, should add means to clean comments on delete
            return ''
        if action.target:
            comment_link = link_tmpl % (absolutize(commented_obj.get_absolute_url()) + "#comment-%s" % subject.id, ' a comment')
            subject = 'to a %s on %s' % (comment_link, _activity_link(commented_obj, plain_text))
        else:
            subject = 'on ' + _activity_link(commented_obj, plain_text)
    elif object_name == 'Rating':
        verb = 'gave'
        subject = '%s a rating of %s' % (_activity_link(subject.content_object,plain_text), subject.rating)
    else:
        subject = _activity_link(subject)
    
    ctx = dict(
        verb= verb,
        timestamp = action.timestamp,
        ago = action.timesince,
        user = username,
        subject = subject
    )
    template = 'mapstory/_activity_item.%s' % ('txt' if plain_text else 'html')
    # user, verb, subject, timestamp, ago
    return loader.render_to_string(template, ctx)

@register.simple_tag
def activity_notifier(user):
    if user.is_authenticated():
        cnted = user.useractivity.other_actor_actions.count()
        if cnted:
            return '<span title="Recent Activity" class="actnot">(%s)</span>' % cnted

@register.simple_tag
def layer_language_selector(layer):
    s = ("selected='selected' ",)
    return "<select name='layer-language'>%s</select>" % "".join(['<option %svalue="%s">%s</option>' % (s + l if layer.language == l[0] else (' ',) + l) for l in ALL_LANGUAGES])
        
@register.simple_tag
def admin_manual():
    url = reverse('mapstory_admin_manual')
    return "<a href='%s' target='admin_manual'>Admin Manual</a>" % (url)
        
@register.simple_tag
def manual_link(target, name):
    url = reverse('mapstory_manual') + "#" + target
    return "<a href='%s' target='manual'>%s</a>" % (url, name)

@register.simple_tag
def manual_include(path):
    return "<div id='manual'>%s</div>" % render_manual(path)


@register.simple_tag
def profile_incomplete(user, show_link=True):
    try:
        incomplete = getattr(user, 'profileincomplete', None)
    except ObjectDoesNotExist:
        incomplete = None
    if incomplete:
        return loader.render_to_string('mapstory/_profile_incomplete.html',
                                   {'incomplete' : incomplete, 'show_link': show_link})
    return ''


@register.simple_tag
def warn_status(req, obj):
    if req.user.is_authenticated() and obj.publish.status == PUBLISHING_STATUS_PRIVATE:
        return loader.render_to_string('maps/_warn_status.html', {})
    return ""

@register.simple_tag
def warn_missing_thumb(obj):
    if not obj.get_thumbnail():
        return loader.render_to_string('maps/_warn_thumbnail.html', {})
    return ""

@register.simple_tag
def pagination(pager, url_name, *args):
    '''pager could be a page or pagination object.'''
    url = reverse(url_name, args=args)
    if not hasattr(pager, 'number'):
        # we're on 'page 0' - lazy load
        pager = Page([], 0, pager)
    return loader.render_to_string('_pagination.html', {'page' : pager, 'url': url})

@register.simple_tag
def user_activity_email_prefs(user):
    active = user.useractivity.notification_preference.lower() + 'active'
    ctx = {'user' : user, active: 'active'}
    return loader.render_to_string('mapstory/user_activity_email_prefs.html', ctx)

@register.inclusion_tag('mapstory/_announcements.html', takes_context=True)
def mapstory_announcements(context):
    return context

@register.simple_tag
def open_graph_meta(obj):
    if isinstance(obj, Layer):
        typename = "StoryLayer"
    else:
        typename = "MapStory"
    return loader.render_to_string('_open_graph_meta.html', {
        'title' : obj.title,
        'type' : typename,
        'url' : obj.get_absolute_url(),
        'image' : obj.get_thumbnail_url(),
        'description' : obj.abstract
    })

# @todo - make geonode location play better
if settings.GEONODE_CLIENT_LOCATION.startswith("http"):
    @register.simple_tag
    def geonode_static(path):
        return settings.GEONODE_CLIENT_LOCATION + path
else:
    geonode_static_prefix = settings.GEONODE_CLIENT_LOCATION.replace(settings.STATIC_URL,"")
    @register.simple_tag
    def geonode_static(path):
        return staticfiles.static(geonode_static_prefix + path)
