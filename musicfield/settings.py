# -*- coding: utf-8 -*-
"""
Django settings/settings.py for mufield development project.
"""
from __future__ import absolute_import
import logging
import celery
from .base import *

# -*- coding: utf-8 -*-
# secret settings

DEBUG = False

TEMPLATE_DEBUG = DEBUG

COMPRESS_ENABLED = not DEBUG

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '' if DEBUG else 'static/')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static/bower_components/jquery/dist/'),
]

MQTT_CONFIGS = {
    'host': 'example.com',  # address-of-mqtt-broker  (default: localhost)
    'port': 1883,  # (default: 1883; with tls, default: 8883)
    'qos': 2,  # (default: 0)
    'retain': False,  # (default is False)
    'tls': False,  # (default: False)
    'cafile': None,  # /path/to/ca/cert.pem
    'certfile': None,  # /path/to/certificate.pem
    'keyfile': None,  # /path/to/key.pem
}

CELERY_DISABLE_RATE_LIMITS = True
CELERYD_CONCURRENCY = 1
CELERY_IGNORE_RESULT = True

CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = {
    'default': {
        "exchange": "default",
        "binding_key": "default",
    },
    'im': {
        'exchange': 'msg',
        'routing_key': 'msg',
    },
    'file': {
        'exchange': 'file',
        'routing_key': 'file',
    },
}

CELERY_ACCEPT_CONTENT = ['pickle']

BROKER_URL = 'amqp://guest:mfadmin@example.com:5672//'

if DEBUG:
    STATICFILES_DIRS.append(os.path.join(BASE_DIR, 'static/'))
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': os.path.join(STATIC_ROOT, 'CACHE/flatpages/'),
            'TIMEOUT': None,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        }
    }

ADMINS = (
    ('hejie', 'kimiscircle@gmail.com'),
)

MANAGERS = ADMINS

# ---------------------------------------------------------------------------- #
# specify custom user model
AUTH_USER_MODEL = 'api.User'
LOGIN_REDIRECT_URL = '/api/docs/'

# gravity value to use when determining song score
SONG_RANK_GRAVITY = 1.8

# ---------------------------------------------------------------------------- #
# `account` settings
# ---------------------------------------------------------------------------- #
# max image file size: 25MB (applies to both accounts and groups)
MAX_IMAGE_SIZE = 25 * 1024 * 1024

# ---------------------------------------------------------------------------- #
# `conversation` settings
# ---------------------------------------------------------------------------- #
# expiry time of groups (in seconds)
GROUP_EXPIRY_TIME_SECONDS = 86400  # 24 hours

# ---------------------------------------------------------------------------- #
# file upload settings
# ---------------------------------------------------------------------------- #
# accepted audio format (mp3) mime types
AUDIO_FORMATS = ["audio/mp3", "audio/mpeg"]
# max audio file size: 15MB
MAX_AUDIO_SIZE = 15 * 1024 * 1024

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'musicfield',
        'USER': 'root',
        'PASSWORD': 'example.com',
        'HOST': 'example.com',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
        },
    },
}

# Django Application definition
DJANGO_APPS = [
    'apps.api',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Third party apps
THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'haystack',
    'whoosh',
    'imagekit',
    'django_jinja',
    'django_user_agents'
]


# Apps specific for this project go here.
LOCAL_APPS = [
    'apps.friendship',
    'apps.friendship.contrib.suggestions',
    'apps.home',
    'apps.chat',
    'apps.csp',  # content security policy
    'apps.flatpages',
    'apps.join',
    'apps.sitemap',
    'apps.online',
    # 'tests',
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'apps.api.middlewares.VersionSwitchMiddleware',
    'apps.api.middlewares.ThreadLocalsMiddleware',
    'apps.chat.middlewares.ExceptionLoggingMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.core.context_processors.static',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',

    'django.template.loaders.eggs.Loader',
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True
    },
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "match_extension", ".html",
        }
    },
]

# ---------------------------------------------------------------------------- #
# `imagekit` settings
# ---------------------------------------------------------------------------- #
# create appropriate thumbnails on source file save only
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = 'imagekit.cachefiles.strategies.Optimistic'
IMAGEKIT_CACHEFILE_DIR = 'cache'
IMAGEKIT_SPEC_CACHEFILE_NAMER = 'imagekit.cachefiles.namers.source_name_as_path'

if DEBUG:
    CSRF_FAILURE_VIEW = 'apps.join.views.csrf_failure'
    DEBUG_TOOLBAR_PATCH_SETTINGS = DEBUG
    THIRD_PARTY_APPS.append('debug_toolbar')
    MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    # https://docs.python.org/2/library/logging.html#logging-levels
    DEBUG_TOOLBAR_CONFIG = {
        'JQUERY_URL': '/static/jquery.min.js',
    }
if COMPRESS_ENABLED:
    # compressor settings
    THIRD_PARTY_APPS.append('compressor')
    COMPRESS_CSS_FILTERS = [
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.CSSMinFilter'
    ]
    # other finders..
    STATICFILES_FINDERS.append('compressor.finders.CompressorFinder')

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MUFIELD_API = {
    'authentication': {
        'user_token_header': 'HTTP_X_MUFIELD_USERTOKEN',
        'chat_token_header': 'HTTP_X_MUFIELD_CHATTOKEN'
    },
    'long_polling': {
        'sleep': 3,
        'iteration': 60
    },
}

# ---------------------------------------------------------------------------- #
# Search engine (`haystack`) settings
# ---------------------------------------------------------------------------- #
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh/mufield_index'),
        'INCLUDE_SPELLING': True,  # include spelling suggestions
    },
}


# rest_framework global processing configuration
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    # only used if the `serializer_class` attribute is not set on a view.
    # Use hyperlinked styles by default
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'PAGINATE_BY': 10,
    'EXCEPTION_HANDLER': 'apps.api.v1.rest.utils.custom_exception_handler'
}

# -*- coding: utf-8 -*-
# fastdfs tracker, multiple tracker supported
FDFS_TRACKER = {
    'host_tuple': ('127.0.0.1', '127.0.0.1'),
    'port': 22122,
    'timeout': 30,
    'name': 'Tracker Pool'
}

SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': '0.6',
    'api_path': '/',
    'enabled_methods': [
        'get',
        'post',
        'put',
        'delete'
    ],
    'api_key': '',
    'is_authenticated': True,
    'is_superuser': False,
    'permission_denied_handler': 'apps.api.v1.rest.utils.permission_denied_handler',
    'info': {
        'contact': 'kimiscircle@gmail.com',
        'description': 'This is MuField application development doc(note expand all api can be slow).',
        'termsOfServiceUrl': ('http://127.0.0.1:8000/' if DEBUG else 'http://mufield.com/') + 'privacy.html',
        'title': 'MusicField',
    },
    'doc_expansion': 'list',
}

# mp3 streaming server config
MP3_STREAM = {
    # lame execution path
    'exe': '/usr/bin/lame',
    # lame encoding bitrate
    'bitrate': 192,
    # for network
    # the port you want to stream on
    'port': 8989,
    # the maximum number of users you want to support
    'maxusers': 10,
    'starttrack': 0,
}

FRIENDS_SUGGESTIONS_IMPORT_RUNNER = 'apps.friendship.contrib.suggestions.backends.runners.AsyncRunner'
OAUTH_ACCESS_SETTINGS = {
    'facebook': {
        'keys': {
            'KEY': 'YOURAPPKEY',
            'SECRET': 'yourappsecretcode',
        },
        'endpoints': {
            # 'authorize': 'https://graph.facebook.com/oauth/authorize',
            'authorize': 'https://www.facebook.com/dialog/oauth/',
            # url above may be blocked in user browser by something like Ghostery so this one is safer
            'access_token': 'https://graph.facebook.com/oauth/access_token',
            'callback': 'friends.contrib.suggestions.views.import_facebook_contacts',
        },
    },
    'twitter': {
        'keys': {
            'KEY': 'YOURAPPKEY',
            'SECRET': 'yourappsecretcode',
        },
        'endpoints': {
            'request_token': 'https://api.twitter.com/oauth/request_token',
            'authorize': 'http://twitter.com/oauth/authorize',
            'access_token': 'https://twitter.com/oauth/request_token',
            'callback': 'friends.contrib.suggestions.views.import_twitter_contacts',
        },
    },
    'yahoo': {
        'keys': {
            'KEY': 'YOURAPPKEY',
            'SECRET': 'yourappsecretcode',
        },
        'endpoints': {
            'request_token': 'https://api.login.yahoo.com/oauth/v2/get_request_token',
            'authorize': 'https://api.login.yahoo.com/oauth/v2/request_auth',
            'access_token': 'https://api.login.yahoo.com/oauth/v2/get_token',
            'callback': 'friends.contrib.suggestions.views.import_yahoo_contacts',
        },
    },
    'linkedin': {
        'keys': {
            'KEY': 'YOURAPPKEY',
            'SECRET': 'yourappsecretcode',
        },
        'endpoints': {
            'request_token': 'https://api.linkedin.com/uas/oauth/requestToken',
            'authorize': 'https://api.linkedin.com/uas/oauth/authorize',
            'access_token': 'https://api.linkedin.com/uas/oauth/accessToken',
            'callback': 'friends.contrib.suggestions.views.import_linkedin_contacts',
        },
    },
}
