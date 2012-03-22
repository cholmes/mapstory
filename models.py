from django.db import models
from django.db.models import Count
from django.db.models import signals
from django.template import defaultfilters

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

from geonode.maps.models import Map

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
    
class Section(models.Model):
    objects = SectionManager()
    
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64)
    maps = models.ManyToManyField(Map)
    order = models.IntegerField(null=True)
    
    def save(self):
        slugtext = self.name.replace('&','and')
        self.slug = defaultfilters.slugify(slugtext)
        if self.order is None:
            self.order = self.id
        models.Model.save(self)
    
    def __unicode__(self):
        return self.name
    
class Link(models.Model):
    name = models.CharField(max_length=64)
    href = models.CharField(max_length=256)
    
class VideoLink(Link):
    title = models.CharField(max_length=32)
    text = models.CharField(max_length=256)
    publish = models.BooleanField(default=False)
    
class ContactDetails(models.Model):
    '''Additional User details'''
    user = models.OneToOneField(User)
    biography = models.CharField(max_length=1024, null=True)
    education = models.CharField(max_length=512, null=True)
    expertise = models.CharField(max_length=256, null=True)
    links = models.ManyToManyField(Link)

def create_contact_details(instance, sender, **kw):
    if kw['created']:
        ContactDetails.objects.create(user = instance)
    
signals.post_save.connect(create_contact_details, sender=User)