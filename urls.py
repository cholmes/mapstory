from django.conf.urls.defaults import *
from django.conf import settings
from staticfiles.urls import staticfiles_urlpatterns
from geonode.sitemap import LayerSitemap, MapSitemap
from geonode.proxy.urls import urlpatterns as proxy_urlpatterns
from geonode.maps.views import new_search_page

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
    #override search urls with specific views
    url(r'^data/search$',new_search_page,kwargs={'bytype':'layer'}),
    url(r'^maps/search$',new_search_page,kwargs={'bytype':'map'}),
    (r'', include('geonode.urls')),
    (r'^data/create_annotations_layer/(?P<mapid>\d+)$','create_annotations_layer'),
)

urlpatterns += proxy_urlpatterns

# Extra static file endpoint for development use
if settings.SERVE_MEDIA:
    urlpatterns += [url(r'^thumbs/(?P<path>.*)$','django.views.static.serve',{
        'document_root' : settings.THUMBNAIL_STORAGE
    })]
    urlpatterns += staticfiles_urlpatterns()
    
