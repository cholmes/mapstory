from itertools import chain

from django.db import models
from django.db.models import Count
from django.db.models import signals

from django.contrib.auth.models import User

from geonode.maps.models import Map
from geonode.maps.models import Layer

class SectionManager(models.Manager):
    def sections_with_maps(self):
        '''Get only those sections that have maps'''
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
            print 'getting',int(topic)
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
    topics = models.ManyToManyField(Topic)
    order = models.IntegerField(null=True)
    
    def _children(self, att):
        field = lambda t: getattr(t,att).filter()
        return set(chain(*[ field(t) for t in self.topics.all()]))
    
    def get_maps(self):
        return self._children('maps')
        
    def get_layers(self):
        return self._children('layers')
    
    def __unicode__(self):
        return 'Section %s' % self.name

    
class Link(models.Model):
    name = models.CharField(max_length=64)
    href = models.CharField(max_length=256)
    
class VideoLink(Link):
    title = models.CharField(max_length=32)
    text = models.CharField(max_length=256)
    publish = models.BooleanField(default=False)
    
class ContactDetail(models.Model):
    '''Additional User details'''
    user = models.OneToOneField(User)
    blurb = models.CharField(max_length=140, null=True)
    biography = models.CharField(max_length=1024, null=True, blank=True)
    education = models.CharField(max_length=512, null=True, blank=True)
    expertise = models.CharField(max_length=256, null=True, blank=True)
    links = models.ManyToManyField(Link)

def create_contact_details(instance, sender, **kw):
    if kw['created']:
        ContactDetail.objects.create(user = instance)
    
signals.post_save.connect(create_contact_details, sender=User)
