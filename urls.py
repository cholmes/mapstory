from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from staticfiles.urls import staticfiles_urlpatterns
from geonode.sitemap import LayerSitemap, MapSitemap
from geonode.proxy.urls import urlpatterns as proxy_urlpatterns

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
    
    # temp urls
    url(r"^mapstory/story/", direct_to_template, {"template": "mapstory/story_detail.html"}, name="story"),
    url(r"^mapstory/manage/", direct_to_template, {"template": "mapstory/story_manage.html"}, name="story_manage"),
    url(r"^mapstory/storyteller/", direct_to_template, {"template": "mapstory/storyteller_detail.html"}, name="storyteller"),
    url(r"^search/search-mapstories/", direct_to_template, {"template": "search/search_mapstories.html"}, name="search_mapstories"),
    url(r"^search/search-layers/", direct_to_template, {"template": "search/search_layers.html"}, name="search_layers"),
    url(r"^map/", direct_to_template, {"template": "maps/map_detail.html"}, name="map_detail"),
)

urlpatterns += proxy_urlpatterns

# Extra static file endpoint for development use
if settings.SERVE_MEDIA:
    urlpatterns += [url(r'^thumbs/(?P<path>.*)$','django.views.static.serve',{
        'document_root' : settings.THUMBNAIL_STORAGE
    })]
    urlpatterns += staticfiles_urlpatterns()
    
