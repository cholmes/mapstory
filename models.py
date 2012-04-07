from itertools import chain

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
    slug = models.SlugField(max_length=64)
    text = models.TextField()
    topics = models.ManyToManyField(Topic,blank=True)
    order = models.IntegerField(null=True)
    
    def _children(self, att):
        field = lambda t: getattr(t,att).filter()
        return set(chain(*[ field(t) for t in self.topics.all()]))
    
    def all_children(self):
        x = self.get_maps() | self.get_layers()
        return x
    
    def get_maps(self):
        return self._children('maps')
        
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
    
class VideoLink(Link):
    title = models.CharField(max_length=32)
    text = models.CharField(max_length=256)
    publish = models.BooleanField(default=False)
    
class ContactDetail(Contact):
    '''Additional User details'''
    blurb = models.CharField(max_length=140, null=True)
    biography = models.CharField(max_length=1024, null=True, blank=True)
    education = models.CharField(max_length=512, null=True, blank=True)
    expertise = models.CharField(max_length=256, null=True, blank=True)
    links = models.ManyToManyField(Link)
    
    
class FavoriteManager(models.Manager):
    
    def favorites_for_user(self, user):
        return self.filter(user=user,in_progress=False)
    
    def inprogress_for_user(self, user):
        return self.filter(user=user,in_progress=True)
    
    def create_favorite(self, content_object, user, in_progress):
        content_type = ContentType.objects.get_for_model(type(content_object))
        favorite = Favorite(
            user=user,
            content_type=content_type,
            object_id=content_object.pk,
            content_object=content_object,
            in_progress=in_progress
            )
        favorite.save()
        return favorite
    
class Favorite(models.Model):
    user = models.ForeignKey(User)
    in_progress = models.BooleanField(default=False)
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

def create_profile(instance, sender, **kw):
    if kw['created']:
        ContactDetail.objects.create(user = instance)
        
signals.post_save.connect(create_profile, sender=User)