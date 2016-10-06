# -*- coding: utf-8 -*-

"""
Django settings for musicfield project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import datetime


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&ku!ebrl5h61ztet=c&ydh+sc9tkq=b70^xbx461)l1pp!lgt6'
HMAC_SECRET_KEY = '4ae214e5cf3fdd2e46467f0a1ff2562d'

BASE_DIR = os.path.dirname(__file__)

ROOT_URLCONF = 'musicfield.urls'

WSGI_APPLICATION = 'musicfield.wsgi.application'

PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))
# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGES = (
    ('en', 'English'),
    #~('zh', 'Chinese'),
)

LANGUAGE_CODE = 'zh-CN'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates/'),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, '../locale/'),
)

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0', 'mufield.com', 'www.mufield.com']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False, #the default configuration is completely overridden
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },

        },
    'handlers': {
        'file_info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
            'filename': os.path.join(BASE_DIR,  '../log/'+datetime.datetime.now().strftime('%Y-%m-%d')+'_INFO.log'),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
            'filename': os.path.join(BASE_DIR,  '../log/'+datetime.datetime.now().strftime('%Y-%m-%d')+'_ERROR.log'),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false']
        }
    },

    'loggers': {
        '': {
            'handlers': ['file_info', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
            },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
            },
        },
    }
