# -*- coding: utf-8 -*-
# Django settings for GeoNode project.
from urllib import urlencode
import os
import geonode

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
GEONODE_ROOT = os.path.dirname(geonode.__file__)

_ = lambda x: x

DEBUG = True
SITENAME = "MapStory"
SITEURL = "http://localhost:8000/"
TEMPLATE_DEBUG = DEBUG

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
                         'NAME': os.path.join(PROJECT_ROOT, 'development.db'),
                         'TEST_NAME': os.path.join(PROJECT_ROOT,
                                                   'development.db')}}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', 'English'),
    ('es', 'Español'),
    ('it', 'Italiano'),
    ('fr', 'Français'),
)

SITE_ID = 1

# Setting a custom test runner to avoid running the tests for some problematic 3rd party apps
TEST_RUNNER='django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
      '--verbosity=2',
      '--cover-erase',
      '--nocapture',
      '--with-coverage',
      '--cover-package=geonode',
      '--cover-inclusive',
      '--cover-tests',
      '--detailed-errors',
      '--with-xunit',
      '--with-id',

# This is very beautiful/usable but requires: pip install rudolf
#      '--with-color',

# The settings below are useful while debugging test failures or errors

#      '--failed',
#      '--pdb-failures',
#      '--stop',
#      '--pdb',
      ]

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'uploaded')

MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'sitestatic')
STATIC_URL = '/static/'
GEONODE_UPLOAD_PATH = MEDIA_ROOT + 'geonode'
GEONODE_CLIENT_LOCATION = STATIC_URL + 'geonode/'
THUMBNAIL_STORAGE = os.path.join(PROJECT_ROOT, 'thumbs')
THUMBNAIL_URL = '/thumbs/'
DEFAULT_MAP_THUMBNAIL = '%stheme/img/img_95x65.png' % STATIC_URL

STATICFILES_STORAGE = 'staticfiles.storage.StaticFilesStorage'

# Additional directories which hold static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'media'),
]

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'myv-y4#7j-d*p-__@j#*3z@!y24fz8%^z2v6atuy4bo9vqr1_a'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.messages.context_processors.messages",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "geonode.maps.context_processors.resource_urls",
    "mapstory.context_processors.page",
    "account.context_processors.account",
)

MIDDLEWARE_CLASSES = (
    'mapstory.util.GlobalRequestMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',    
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

# This isn't required for running the geonode site, but it when running sites that inherit the geonode.settings module.
LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, "locale"),
    os.path.join(PROJECT_ROOT, "maps", "locale"),
)

ROOT_URLCONF = 'mapstory.urls'

# Note that Django automatically includes the "templates" dir in all the
# INSTALLED_APPS, se there is no need to add maps/templates or admin/templates
TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT,"templates"),
    os.path.join(GEONODE_ROOT,"templates"),
    os.path.join(GEONODE_ROOT,'..'), # this allows the extend and override pattern
)

# The FULLY QUALIFIED url to the GeoServer instance for this GeoNode.
GEOSERVER_BASE_URL = "http://localhost:8001/geoserver/"

# The username and password for a user that can add and edit layer details on GeoServer
GEOSERVER_CREDENTIALS = "geoserver_admin", SECRET_KEY 

# The FULLY QUALIFIED url to the GeoNetwork instance for this GeoNode
GEONETWORK_BASE_URL = "http://localhost:8001/geonetwork/"

# The username and password for a user with write access to GeoNetwork
GEONETWORK_CREDENTIALS = "admin", "admin"

AUTHENTICATION_BACKENDS = ('geonode.core.auth.GranularBackend',)

GOOGLE_API_KEY = "ABQIAAAAkofooZxTfcCv9Wi3zzGTVxTnme5EwnLVtEDGnh-lFVzRJhbdQhQgAhB1eT_2muZtc0dl-ZSWrtzmrw"
LOGIN_REDIRECT_URL = "/"

DEFAULT_LAYERS_OWNER='admin'

# Where should newly created maps be focused?
DEFAULT_MAP_CENTER = (-84.7, 12.8)

# How tightly zoomed should newly created maps be?
# 0 = entire world;
# maximum zoom is between 12 and 15 (for Google Maps, coverage varies by area)
DEFAULT_MAP_ZOOM = 7

DEFAULT_LAYER_SOURCE = {
    "ptype":"gxp_wmscsource",
    "url":"/geoserver/wms",
    "restUrl": "/gs/rest"
}

MAP_BASELAYERS = [
    {
        "source": {"ptype": "gx_olsource"},
        "type":"OpenLayers.Layer",
        "args":["No background"],
        "visibility": False,
        "fixed": True,
        "group":"background"
    },
    {
        "source": {"ptype":"gx_olsource"},
        "type":"OpenLayers.Layer.OSM",
        "args":["OpenStreetMap"],
        'title': 'This is the title',
        "visibility": True,
        "fixed": True,
        "group":"background"
    },

    {
        "source": {"ptype":"gx_olsource"},
        "type":"OpenLayers.Layer.WMS",
        "group":"background",
        "visibility": False,
        "fixed": True,
        "args":[
            "Naked Earth",
            "http://maps.opengeo.org/geowebcache/service/wms",
            {
                "layers":["Wayne"],
                "format":"image/png",
                "tiled": True,
                "tilesOrigin":[-20037508.34, -20037508.34]
            },
            {"buffer":0}
        ]
    },
    {
        'source': {
            'ptype': 'gxp_mapquestsource',
            'hidden': True
        },
        'name': 'naip',
        'title': 'Satellite Imagery',
        'group': 'background',
        'args': ['Satellite Imagery']
    },

]

# use new uploader
USE_UPLOADER=True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    'django.contrib.webdesign',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django_extensions',
    'announcements',
    'flatblocks',
    'flag',
    'hitcount',
    'account',
    'kaleo',
    'profiles',
    'avatar',
    'dialogos',
    'mptt',
    'agon_ratings',
    'taggit',
    'mapstory',
    'geonode.core',
    'geonode.maps',
    'geonode.proxy',
    'geonode.simplesearch',
    'geonode.upload',
    'geonode',
    'mapstory.watchdog',
    'actstream',
    'mailer',
    'oembed',
)

def get_user_url(u):
    from django.contrib.sites.models import Site
    s = Site.objects.get_current()
    return "http://" + s.domain + "/profiles/" + u.username


ABSOLUTE_URL_OVERRIDES = {
    'auth.user': get_user_url
}

AUTH_PROFILE_MODULE = 'mapstory.ContactDetail'
REGISTRATION_OPEN = False

SERVE_MEDIA = DEBUG;

#Import uploaded shapefiles into a database such as PostGIS?
DB_DATASTORE=False

#Database datastore connection settings
DB_DATASTORE_NAME = ''
DB_DATASTORE_USER = ''
DB_DATASTORE_PASSWORD = ''
DB_DATASTORE_HOST = ''
DB_DATASTORE_PORT = ''
DB_DATASTORE_TYPE=''

# Agon Ratings
AGON_RATINGS_CATEGORY_CHOICES = {
    "maps.Map": {
        "map": "How good is this map?"
    },
    "maps.Layer": {
        "layer": "How good is this layer?"
    },
}

USERS_TO_EXCLUDE_IN_LISTINGS = [
    'admin',
    'geonode'
]

LAYER_EXCLUSIONS = [
    '_map_\d+_annotations'
]

SIMPLE_SEARCH_SETTINGS = {
    'layer_exclusions' : LAYER_EXCLUSIONS,
    'extra_query' : ['bytopic','bysection'],
    'extension' : 'mapstory.simplesearch'
}

USERS_TO_EXCLUDE_IN_LISTINGS = []

DESIGN_MODE = False

ENABLE_ANALYTICS = False

AVATAR_DEFAULT_URL = "theme/img/storyteller.png"

HITCOUNT_KEEP_HIT_ACTIVE = { 'days': 1 }
HITCOUNT_HITS_PER_IP_LIMIT = 0
HITCOUNT_EXCLUDE_USER_GROUP = ( 'Editor', )

UPLOADER_SHOW_TIME_STEP = True

ACTSTREAM_SETTINGS = {
    'MODELS': (
               'auth.user',
               'mapstory.contactdetail',
               'maps.layer',
               'maps.map',
               'dialogos.comment',
              ),
}

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: '/mapstory/storyteller/%s' % u.username
}

#EMAIL_BACKEND = "mailer.backend.DbBackend"

ENABLE_SOCIAL_LOGIN = False

try:
    from local_settings import *
except ImportError:
    pass

if ENABLE_SOCIAL_LOGIN:
    INSTALLED_APPS = INSTALLED_APPS + (
        'social_auth',
        'provider',
        'provider.oauth2',
    )
    AUTHENTICATION_BACKENDS = (
        'social_auth.backends.twitter.TwitterBackend',
        'social_auth.backends.facebook.FacebookBackend',
        'social_auth.backends.google.GoogleOAuth2Backend',
        'social_auth.backends.yahoo.YahooBackend',
        'social_auth.backends.contrib.github.GithubBackend',
    ) + AUTHENTICATION_BACKENDS
