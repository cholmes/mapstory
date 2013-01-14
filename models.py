from itertools import chain
import random
import operator
import re
import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count
from django.db.models import signals
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.template import defaultfilters

from django.contrib.auth.models import User

from geonode.core.models import AUTHENTICATED_USERS
from geonode.core.models import ANONYMOUS_USERS
from geonode.maps.models import Contact
from geonode.maps.models import Map
from geonode.maps.models import Layer
from geonode.maps.models import LayerManager
from geonode.upload.signals import upload_complete

from mapstory import gwc_config

from hitcount.models import HitCount
from agon_ratings.models import OverallRating
from agon_ratings.categories import RATING_CATEGORY_LOOKUP

_logger = logging.getLogger('mapstory.models')
def _debug(msg,*args):
    _logger.debug(msg,*args)
_debug_enabled = _logger.isEnabledFor(logging.DEBUG)

'''Settings API - allow regular expressions to filter our layer name results'''
if hasattr(settings,'LAYER_EXCLUSIONS'):
    _exclude_patterns = settings.LAYER_EXCLUSIONS
    _exclude_regex = [ re.compile(e) for e in _exclude_patterns ]
_layer_name_filter = reduce(operator.or_,[ Q(name__regex=f) for f in _exclude_patterns])

def filtered_layers_query(self):
    return self.get_query_set().exclude(_layer_name_filter)
LayerManager.filtered = filtered_layers_query

def get_view_cnt_for(obj):
    '''Provide cached access to view cnts'''
    return get_view_cnts(type(obj)).get(obj.id,0)

def get_view_cnts(model):
    '''Provide cached access to view counts for a given model.
    The current approach is to cache all values. An alternate approach, should
    there be too many, is to partition by 'id mod some bucket size'.
    '''
    key = 'view_cnt_%s' % model.__name__
    cached = cache.get(key)
    hit = True
    if _debug_enabled:
        ts = time.time()
    if not cached:
        hit = False
        ctype = ContentType.objects.get_for_model(model)
        hits = HitCount.objects.filter(content_type=ctype)
        cached = dict([ (int(h.object_pk),h.hits) for h in hits])
        cache.set(key,cached)
    if _debug_enabled:
        _debug('view cnts for %s in %s, cached: %s',model.__name__,time.time() - ts,hit)
    return cached

def get_ratings(model):
    '''cached results for an objects rating'''
    key = 'overall_rating_%s' % model.__name__
    results = cache.get(key)
    if not results:
        # this next big is some hacky stuff related to rankings
        choice = model.__name__.lower()
        category = RATING_CATEGORY_LOOKUP.get(
            "%s.%s-%s" % (model._meta.app_label, model._meta.object_name, choice)
        ) 
        try:
            ct = ContentType.objects.get_for_model(model)
            ratings = OverallRating.objects.filter(
                content_type = ct,
                category = category
            )
            results = dict([ (r.object_id, r.rating) or 0 for r in ratings])
            cache.set(key, results)
        except OverallRating.DoesNotExist:
            return {}
    return results


def get_related_stories(obj):
    if isinstance(obj, Section):
        topics = obj.topics.all()
    else:
        topics = list(obj.topic_set.all())
    maps = []
    # @todo gather from all topics and respective sections
    sections = topics and topics[0].section_set.all() or None
    if topics and sections:
        sec = sections[0]
        maps = sec.get_maps()
        if isinstance(obj, Map):
            maps = maps.exclude(id=obj.id)
    return maps


class SectionManager(models.Manager):
    def sections_with_maps(self):
        '''@todo this is broken - Get only those sections that have maps'''
        return self.all().annotate(num_maps=Count('maps')).filter(num_maps__gt=0)


class TopicManager(models.Manager):
    def tag(self, obj, topic, allow_create=False):
        if allow_create:
            topic,_ = self.get_or_create(name=topic)
        else:
            topic = self.get(pk=int(topic))
        related = isinstance(obj, Map) and topic.maps or topic.layers
        # @todo - only allowing one topic per item (UI work needed)
        obj.topic_set.clear()
        related.add(obj)
        topic.save()
        
    
class Topic(models.Model):
    objects = TopicManager()
    
    name = models.CharField(max_length=64)
    layers = models.ManyToManyField(Layer,blank=True)
    maps = models.ManyToManyField(Map,blank=True)
    
    def __unicode__(self):
        return 'Topic - %s' % self.name
    
     
class Section(models.Model):
    objects = SectionManager()
    
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64,blank=True)
    text = models.TextField(null=True)
    topics = models.ManyToManyField(Topic,blank=True)
    order = models.IntegerField(null=True,blank=True)
    
    def _children(self, model, **kw):
        query = model.objects.filter(**kw)
        return query.filter(topic__in=self.topics.all())
    
    def all_children(self):
        ch = list(self.get_maps())
        ch.extend(self.get_layers())
        return ch
    
    def get_maps(self):
        return self._children(Map, publish__status=PUBLISHING_STATUS_PUBLIC)
        
    def get_layers(self):
        return self._children(Layer, publish__status=PUBLISHING_STATUS_PUBLIC)
    
    def save(self,*args,**kw):
        slugtext = self.name.replace('&','and')
        self.slug = defaultfilters.slugify(slugtext)
        if self.order is None:
            self.order = self.id
        models.Model.save(self)
        
    def maps_pager(self, page_size=6):
        '''make it easy to get a paginator in a template'''
        return Paginator(list(self.get_maps()), page_size)
        
    def get_absolute_url(self):
        return reverse('section_detail',args=[self.slug])
    
    def __unicode__(self):
        return 'Section %s' % self.name

    
class Link(models.Model):
    name = models.CharField(max_length=64)
    href = models.CharField(max_length=256)
    order = models.IntegerField(default=0, blank=True, null=True)

_VIDEO_LOCATION_FRONT_PAGE = 'FP'
_VIDEO_LOCATION_HOW_TO = 'HT'
_VIDEO_LOCATION_REFLECTIONS = 'RF'
_VIDEO_LOCATION_CHOICES = [
    (_VIDEO_LOCATION_FRONT_PAGE,'Front Page'),
    (_VIDEO_LOCATION_HOW_TO,'How To'),
    (_VIDEO_LOCATION_REFLECTIONS,'Reflections')
]
    
class VideoLinkManager(models.Manager):
    def front_page_video(self):
        videos = VideoLink.objects.filter(publish=True,location=_VIDEO_LOCATION_FRONT_PAGE)
        if not videos:
            videos = VideoLink.objects.all()
        if not videos:
            return None
        return random.choice(videos)
    def how_to_videos(self):
        return VideoLink.objects.filter(publish=True,location=_VIDEO_LOCATION_HOW_TO)
    def reflections_videos(self):
        return VideoLink.objects.filter(publish=True,location=_VIDEO_LOCATION_REFLECTIONS)

class VideoLink(Link):
    objects = VideoLinkManager()
    
    title = models.CharField(max_length=32)
    text = models.CharField(max_length=350)
    publish = models.BooleanField(default=False)
    location = models.CharField(max_length=2, choices=_VIDEO_LOCATION_CHOICES)

_NOTIFICATION_PREFERENCES = [
    ('E','Email'),
    ('S','Daily Summary'),
    ('N','None')
]
class UserActivity(models.Model):
    user = models.OneToOneField(User)
    # automatically tracked actions
    other_actor_actions = models.ManyToManyField('actstream.Action')
    notification_preference = models.CharField(max_length=1, default='N', choices=_NOTIFICATION_PREFERENCES)


class ContactDetail(Contact):
    '''Additional User details'''
    blurb = models.CharField(max_length=140, null=True)
    biography = models.CharField(max_length=1024, null=True, blank=True)
    education = models.CharField(max_length=512, null=True, blank=True)
    expertise = models.CharField(max_length=256, null=True, blank=True)
    links = models.ManyToManyField(Link)

    def audit(self):
        '''return a list of what is needed to 'complete' the profile'''
        incomplete = []
        if self.user.avatar_set.filter(primary=True).count() == 0:
            incomplete.append('Picture/Avatar')
        if not all([self.user.first_name, self.user.last_name]):
            incomplete.append('Full Name')
        if not self.blurb:
            incomplete.append('Blurb')
        return incomplete

    def update_audit(self):
        incomplete = self.audit()
        if incomplete:
            pi, _ = ProfileIncomplete.objects.get_or_create(user=self.user)
            pi.message = ('Please ensure the following '
            'fields are complete: %s'
            ) % ', '.join(incomplete)
            pi.save()
        else:
            ProfileIncomplete.objects.filter(user=self.user_id).delete()


class ProfileIncomplete(models.Model):
    '''Track incomplete user profiles'''
    user = models.OneToOneField(User)
    message = models.TextField()


class Resource(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64,blank=True)
    order = models.IntegerField(null=True,blank=True)
    text = models.TextField(null=True)

    def save(self,*args,**kw):
        slugtext = self.name.replace('&','and')
        self.slug = defaultfilters.slugify(slugtext)
        if self.order is None:
            self.order = self.id
        models.Model.save(self)
        
    def get_absolute_url(self):
        return reverse('mapstory_resource',args=[self.slug])
    
class FavoriteManager(models.Manager):
    
    def favorites_for_user(self, user):
        return self.filter(user=user)
    
    def favorite_maps_for_user(self, user):
        content_type = ContentType.objects.get_for_model(Map)
        return self.favorites_for_user(user).filter(content_type=content_type)
    
    def create_favorite(self, content_object, user):
        content_type = ContentType.objects.get_for_model(type(content_object))
        favorite = Favorite(
            user=user,
            content_type=content_type,
            object_id=content_object.pk,
            content_object=content_object,
            )
        favorite.save()
        return favorite
    
class Favorite(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    created_on = models.DateTimeField(auto_now_add=True)
    
    objects = FavoriteManager()

    class Meta:
        verbose_name = 'favorite'
        verbose_name_plural = 'favorites'
        unique_together = (('user', 'content_type', 'object_id'),)
    
    def __unicode__(self):
        return "%s likes %s" % (self.user, self.content_object)
    
PUBLISHING_STATUS_PRIVATE = "Private"
PUBLISHING_STATUS_LINK = "Link"
PUBLISHING_STATUS_PUBLIC = "Public"
PUBLISHING_STATUS_CHOICES = [
    (PUBLISHING_STATUS_PRIVATE,PUBLISHING_STATUS_PRIVATE),
    (PUBLISHING_STATUS_LINK,PUBLISHING_STATUS_LINK),
    (PUBLISHING_STATUS_PUBLIC,PUBLISHING_STATUS_PUBLIC)
]

class PublishingStatusMananger(models.Manager):
    def get_public(self, user, model):
        return model.objects.filter(owner=user, publish__status=PUBLISHING_STATUS_PUBLIC)
    def get_in_progress(self, user, model):
        if model == Layer:
            # don't show annotations
            q = model.objects.filtered()
        else:
            q = model.objects.all()
        q = q.filter(owner=user)
        return q.exclude(publish__status=PUBLISHING_STATUS_PUBLIC)
    def get_or_create_for(self, obj):
        if isinstance(obj, Map):
            status, _ = self.get_or_create(map=obj)
        else:
            status, _ = self.get_or_create(layer=obj)
        return status
    def set_status(self, obj, status):
        stat = self.get_or_create_for(obj)
        stat.status = status
        stat.save()

class PublishingStatus(models.Model):
    '''This is a denormalized model - could have gone with a content-type
    but it seemed to make the queries much more complex than needed.
    
    Each entry should either have a map or a layer.
    '''
    
    objects = PublishingStatusMananger()
    
    map = models.OneToOneField(Map,related_name='publish',null=True)
    layer = models.OneToOneField(Layer,related_name='publish',null=True)
    status = models.CharField(max_length=8,choices=PUBLISHING_STATUS_CHOICES,default=PUBLISHING_STATUS_PRIVATE)
    
    def check_related(self):
        if self.map:
            layers = self.map.local_layers
            owner = self.map.owner
            if len(set([owner]) | set([l.owner for l in layers])) > 1:
                return [ l for l in layers if l.owner == owner ]

    def update_related(self, ignore_owner=False):
        if self.map:
            for l in self.map.local_layers:
                if ignore_owner or l.owner == self.map.owner:
                    l.publish.status = self.status
                    l.publish.clean_fields()
                    l.publish.save()

    def save(self,*args,**kw):
        obj = self.layer or self.map
        level = obj.LEVEL_READ
        if self.status == PUBLISHING_STATUS_PRIVATE:
            level = obj.LEVEL_NONE
        obj.set_gen_level(ANONYMOUS_USERS, level)
        obj.set_gen_level(AUTHENTICATED_USERS, level)
        if obj.owner: # usually won't happen except in fixture loading?
            obj.set_user_level(obj.owner, obj.LEVEL_ADMIN)
        models.Model.save(self, *args)
        
        
def audit_layer_metadata(layer):
    '''determine if metadata is complete to allow publishing'''
    return all([
        layer.title,
        layer.abstract,
        layer.purpose,
        layer.keyword_list(),
        layer.language,
        layer.supplemental_information,
        layer.data_quality_statement,
        layer.topic_set.all()
    ]) and layer.topic_set.count()

    
def user_saved(instance, sender, **kw):
    if kw['created']:
        ContactDetail.objects.create(user = instance)

def create_publishing_status(instance, sender, **kw):
    if kw['created']:
        PublishingStatus.objects.get_or_create_for(instance)
        
def set_publishing_private(**kw):
    instance = kw.get('layer')
    PublishingStatus.objects.set_status(instance, PUBLISHING_STATUS_PRIVATE)
    
def configure_gwc(**kw):
    instance = kw.get('layer')
    gwc_config.configure_layer(instance.typename)
        
def create_hitcount(instance, sender, **kw):
    if kw['created']:
        content_type = ContentType.objects.get_for_model(instance)
        HitCount.objects.create(content_type=content_type, object_pk=instance.pk)
        
def clear_acl_cache(instance, sender, **kw):
    if kw['created'] and instance.owner:
        # this will only handle the owner's cached acls - other users will be
        # out of luck for the timeout period - likely not to be an issue
        key = 'layer_acls_%s' % instance.owner.id
        cache.delete(key)


def remove_favorites(instance, sender, **kw):
    ct = ContentType.objects.get_for_model(instance)
    Favorite.objects.filter(content_type=ct, object_id=instance.id).delete()
    
def create_user_activity(sender, instance, created, **kw):
    if created:
        UserActivity.objects.create(user=instance)
        

signals.post_save.connect(create_user_activity, sender=User)

# make sure any favorites are also deleted
signals.pre_delete.connect(remove_favorites, sender=Map)
signals.pre_delete.connect(remove_favorites, sender=Layer)

signals.post_save.connect(user_saved, sender=User)
signals.post_save.connect(create_publishing_status, sender=Map)
signals.post_save.connect(create_publishing_status, sender=Layer)
# @annoyatron - core upload sets permissions after saving the layer
# this signal allows layering the publishing status behavior on top
# this is not needed for maps
upload_complete.connect(set_publishing_private, sender=None)
upload_complete.connect(configure_gwc, sender=None)
# @annoyatron2 - after map is saved, set_default_permissions is called - hack this
Map.set_default_permissions = lambda s: None

# ensure hit count records are created up-front
signals.post_save.connect(create_hitcount, sender=Map)
signals.post_save.connect(create_hitcount, sender=Layer)

# @todo hackity hack - throw out acl cache on Layer addition
signals.post_save.connect(clear_acl_cache, sender=Layer)
