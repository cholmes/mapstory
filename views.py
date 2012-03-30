from geonode.maps.models import Map
from geonode.maps.models import Layer
from geonode.maps.models import Thumbnail

from mapstory.models import VideoLink
from mapstory.models import Section

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import signals
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import loader
from django.contrib.contenttypes.models import ContentType

import os
import random

def alerts(req): 
    return render_to_response('mapstory/alerts.html', RequestContext(req))

def index(req):
    # resolve video to use
    # two modes of operation here
    # 1) don't specify publish and one will randomly be chosen
    # 2) specify one or more publish links and one will be chosen
    videos = VideoLink.objects.filter(publish=True)
    if not videos:
        videos = VideoLink.objects.all()
    video = random.choice(videos)
    
    tiles = ''.join( [ _render_map_tile(m) for m in get_map_carousel_maps()] )
    
    return render_to_response('index.html', RequestContext(req,{
        "video" : video,
        "tiles" : tiles
    }))

def donate(req):
    return render_to_response('mapstory/donate.html', RequestContext(req))

def get_map_carousel_maps():
    '''Get the carousel ids/thumbnail dict either
    1. as specified (model does not exist yet...)
    2. by some rating/view ranking (not implemented)
    3. any map that has a thumbnail (current)
    '''
    
    # get all Map thumbnails
    thumb_type = ContentType.objects.get_for_model(Map)
    thumbs = Thumbnail.objects.filter(content_type__pk=thumb_type.id)
    # trim this down to a smaller set
    thumbs = random.sample(thumbs, min(10,len(thumbs)))
    # and make sure they have a valid file path
    return [ t.content_object for t in thumbs if os.path.exists(t.get_thumbnail_path())]

def map_tiles(req):
    maps = get_map_carousel_maps()
    return HttpResponse(''.join( [ _render_map_tile(m) for m in maps] ))

def _render_map_tile(obj,thumb=None,req=None):
    if not thumb:
        thumb = obj.get_thumbnail()
    if thumb:
        thumb = thumb.get_thumbnail_url()
    else:
        thumb = '%stheme/img/silk/map.png' % settings.STATIC_URL
    if obj.owner.first_name:
        author = '%s %s' % (obj.owner.first_name,obj.owner.last_name)
    else:
        author = obj.owner.username
        
    author_link = reverse('profiles.views.profile_detail', args=(obj.owner.username,))
        
    ctx = {
        'title' : obj.title,
        'author' : author,
        'author_link' : author_link,
        'thumb' : thumb,
        'map_view' : reverse( 'geonode.maps.views.map_controller' , args=[obj.id]),
        'last_modified' : obj.last_modified.strftime('%b %d %Y')
    }
    
    template = 'mapstory/tile.html'
    if req:
        return render_to_response(template, RequestContext(req,ctx))
    return loader.render_to_string(template,ctx)

def map_tile(req, mapid):
    obj = get_object_or_404(Map,pk=mapid)
    return _render_map_tile(obj,req=req)

@login_required
def set_section(req):
    if req.method != 'POST':
        return HttpResponse('POST required',status=400)
    mapid = req.POST['map']
    mapobj = get_object_or_404(Map, pk=mapid)
    if mapobj.owner != req.user or not req.user.has_perm('mapstory.change_section'):
        return HttpResponse('Not sufficient permissions',status=401)
    sectionid = req.POST['section']
    get_object_or_404(Section, pk=sectionid)
    Section.objects.add_to_section(sectionid, mapobj)
    return HttpResponse('OK', status=200)

def about_storyteller(req, username):
    user = get_object_or_404(User, username=username)
    return render_to_response('mapstory/about_storyteller.html', RequestContext(req,{
        "user" : user,
    }))

@login_required
def create_annotations_layer(req, mapid):
    '''Create an annotations layer with the predefined schema.
    
    @todo ugly hack - using existing view to allow this
    '''
    from geonode.maps.views import _create_layer
    
    mapobj = get_object_or_404(Map,pk=mapid)
    
    if req.method != 'POST':
        return HttpResponse('POST required',status=400)
    
    if mapobj.owner != req.user:
        return HttpResponse('Not owner of map',status=401)
    
    atts = [
        #name, type, nillable
        ('title','java.lang.String',False),
        ('content','java.lang.String',False),
        ('the_geom','com.vividsolutions.jts.geom.Geometry',True),
        ('start_time','java.lang.Long',True),
        ('end_time','java.lang.Long',True),
        ('in_timeline','java.lang.Boolean',True),
        ('in_map','java.lang.Boolean',True),
        ('appearance','java.lang.String',True),
    ]
    
    # @todo remove this when hack is resolved. build our spec string
    atts = ','.join([ ':'.join(map(str,a)) for a in atts])
    
    return _create_layer(
        req.user,
        name = "_map_%s_annotations" % mapid,
        srs = 'EPSG:4326', # @todo how to obtain this in a nicer way...
        attributes = atts,
        skip_style = True
    )
    
def _remove_annotation_layer(sender, instance, **kw):
    try:
        Layer.objects.get(name='_map_%s_annotations' % instance.id)
    except Layer.DoesNotExist:
        pass

signals.pre_delete.connect(_remove_annotation_layer, sender=Map)