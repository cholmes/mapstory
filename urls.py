from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from staticfiles.urls import staticfiles_urlpatterns
from geonode.sitemap import LayerSitemap, MapSitemap
from geonode.proxy.urls import urlpatterns as proxy_urlpatterns
from mapstory.models import *
from geonode.maps.models import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('geonode',)
}

sitemaps = {
    "layer": LayerSitemap,
    "map": MapSitemap
}

urlpatterns = patterns('mapstory.views',
    (r'^(?:index/?)?$', 'index'),

    (r'', include('geonode.simplesearch.urls')), # put this first to ensure search urls priority
    (r'', include('geonode.urls')),
    (r'^data/create_annotations_layer/(?P<mapid>\d+)$','create_annotations_layer'),
    url(r'^mapstory/donate$','donate',name='donate'),
    url(r'^mapstory/alerts$','alerts',name='alerts'),
    url(r'^mapstory/tile/(?P<mapid>\d+)$','map_tile',name='map_tile'),
    url(r'^mapstory/tiles$','map_tiles',name='map_tiles'),
    url(r'^mapstory/storyteller/(?P<username>\w+)$','about_storyteller',name='about_storyteller'),
    
    # semi-temp urls
    url(r'^mapstory/topics/(?P<layer_or_map>\w+)/(?P<layer_or_map_id>\d+)$','topics_api',name='topics_api'),
    url(r'^mapstory/comment/(?P<layer_or_map_id>\d+)/(?P<comment_id>\d+)$','delete_story_comment',name='delete_story_comment'),
    url(r'^favorite/map/(?P<id>\d+)$','favorite',{'layer_or_map':'map'}, name='add_favorite_map'),
    url(r'^favorite/map/in_progress(?P<id>\d+)$','favorite',{'layer_or_map':'map','in_progress':True}, name='add_inprogress_map',),
    url(r'^favorite/layer/(?P<id>\d+)$','favorite',{'layer_or_map':'layer'}, name='add_favorite_layer'),
    url(r'^favorite/layer/in_progress(?P<id>\d+)$','favorite',{'layer_or_map':'layer','in_progress':True}, name='add_inprogress_layer',),
    url(r'^favorite/(?P<id>\d+)/delete$','delete_favorite',name='delete_favorite'),

    # ugh, overrides
    url(r'^(?P<layername>[^/]*)/metadata$', 'layer_metadata', name="layer_metadata"),

    # temp urls
    url(r"^mapstory/story/", direct_to_template, {"template": "mapstory/story_detail.html"}, name="story"),
    url(r"^mapstory/manage/", direct_to_template, {"template": "mapstory/story_manage.html"}, name="story_manage"),
    url(r"^mapstory/storyteller/", direct_to_template, {"template": "mapstory/storyteller_detail.html"}, name="storyteller"),
    url(r"^search/search-mapstories/", direct_to_template, {"template": "search/search_mapstories.html"}, name="search_mapstories"),
    url(r"^layer/manage/", direct_to_template, {"template": "mapstory/layer_manage.html"}, name="layer_manage"),
    url(r"^map/", direct_to_template, {"template": "maps/map_detail.html"}, name="map_detail"),
)

urlpatterns += proxy_urlpatterns

# Extra static file endpoint for development use
if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^thumbs/(?P<path>.*)$','django.views.static.serve',{
            'document_root' : settings.THUMBNAIL_STORAGE,
        })
    )
    urlpatterns += staticfiles_urlpatterns()
    
