from itertools import chain
import random

from django.db import models
from django.db.models import Count
from django.db.models import signals
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.template import defaultfilters

from django.contrib.auth.models import User

from geonode.maps.models import Contact
from geonode.maps.models import Map
from geonode.maps.models import Layer

class SectionManager(models.Manager):
    def sections_with_maps(self):
        '''@todo this is broken - Get only those sections that have maps'''
        return self.all().annotate(num_maps=Count('maps')).filter(num_maps__gt=0)
    def add_to_section(self, sid, amap):
        '''business logic for being in a section - exclusive for the moment'''
        for s in self.filter(maps__id = amap.id):
            s.maps.remove(amap)
            s.save()
        s = self.get(id = sid)
        s.maps.add(amap)
        s.save()
        
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
    layers = models.ManyToManyField(Layer)
    maps = models.ManyToManyField(Map)
    
    def __unicode__(self):
        return 'Topic - %s' % self.name
    
     
class Section(models.Model):
    objects = SectionManager()
    
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64,blank=True)
    text = models.TextField(null=True)
    topics = models.ManyToManyField(Topic,blank=True)
    order = models.IntegerField(null=True,blank=True)
    
    def _children(self, att, **kw):
        field = lambda t: getattr(t,att).filter(**kw)
        return set(chain(*[ field(t) for t in self.topics.all()]))
    
    def all_children(self):
        x = self.get_maps() | self.get_layers()
        return x
    
    def get_maps(self):
        return self._children('maps', publish__status='Public')
        
    def get_layers(self):
        return self._children('layers')
    
    def save(self,*args,**kw):
        slugtext = self.name.replace('&','and')
        self.slug = defaultfilters.slugify(slugtext)
        if self.order is None:
            self.order = self.id
        models.Model.save(self)
        
    def get_absolute_url(self):
        return reverse('section_detail',args=[self.slug])
    
    def __unicode__(self):
        return 'Section %s' % self.name

    
class Link(models.Model):
    name = models.CharField(max_length=64)
    href = models.CharField(max_length=256)
    
_VIDEO_LOCATION_FRONT_PAGE = 'FP'
_VIDEO_LOCATION_HOW_TO = 'HT'
_VIDEO_LOCATION_CHOICES = [
    (_VIDEO_LOCATION_FRONT_PAGE,'Front Page'),
    (_VIDEO_LOCATION_HOW_TO,'How To')
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

class VideoLink(Link):
    objects = VideoLinkManager()
    
    title = models.CharField(max_length=32)
    text = models.CharField(max_length=350)
    publish = models.BooleanField(default=False)
    location = models.CharField(max_length=2, choices=_VIDEO_LOCATION_CHOICES)
    
class ContactDetail(Contact):
    '''Additional User details'''
    blurb = models.CharField(max_length=140, null=True)
    biography = models.CharField(max_length=1024, null=True, blank=True)
    education = models.CharField(max_length=512, null=True, blank=True)
    expertise = models.CharField(max_length=256, null=True, blank=True)
    links = models.ManyToManyField(Link)
    
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
    
_MAP_PUBLISHING_IN_PROGRESS = "In Progress"
_MAP_PUBLISHING_PUBLIC = "Public"
_MAP_PUBLISHING_CHOICES = [
    (_MAP_PUBLISHING_IN_PROGRESS,_MAP_PUBLISHING_IN_PROGRESS),
    (_MAP_PUBLISHING_PUBLIC,_MAP_PUBLISHING_PUBLIC),
]

class PublishingStatusMananger(models.Manager):
    def get_public(self, user):
        return Map.objects.filter(owner=user, publish__status=_MAP_PUBLISHING_PUBLIC)
    def get_in_progress(self, user):
        return Map.objects.filter(owner=user, publish__status=_MAP_PUBLISHING_IN_PROGRESS)
    def set_status(self, mapobj, status):
        status = self.get_or_create(map_obj)
        status.status = status
        status.save()
    def set_public(self,map_obj):
        self.set_status(_MAP_PUBLISHING_PUBLIC)
    def set_in_progress(self,map_obj):
        self.set_status(_MAP_PUBLISHING_IN_PROGRESS)

class PublishingStatus(models.Model):
    objects = PublishingStatusMananger()
    
    map = models.OneToOneField(Map,related_name='publish')
    status = models.CharField(max_length=16,choices=_MAP_PUBLISHING_CHOICES,default=_MAP_PUBLISHING_IN_PROGRESS)
    
    def get_toggle_value(self):
        if self.status == _MAP_PUBLISHING_IN_PROGRESS: 
            return _MAP_PUBLISHING_PUBLIC
        return _MAP_PUBLISHING_IN_PROGRESS
    
def create_profile(instance, sender, **kw):
    if kw['created']:
        ContactDetail.objects.create(user = instance)
        
def create_publishing_status(instance, sender, **kw):
    if kw['created']:
        PublishingStatus.objects.create(map = instance)
        
signals.post_save.connect(create_profile, sender=User)
signals.post_save.connect(create_publishing_status, sender=Map)