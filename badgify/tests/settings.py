# -*- coding: utf-8 -*-
import os
import django

ROOT = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SITE_ID = 1

DEBUG = True

MIDDLEWARE_CLASSES = ()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'badgify',
    'badgify.tests',
]

AUTH_USER_MODEL = 'tests.BadgifyUser'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(ROOT, 'media')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(ROOT, 'static')

SECRET_KEY = 'blabla'

ROOT_URLCONF = 'badgify.urls'

TEMPLATE_DIRS = (
    os.path.join(ROOT, 'templates'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'stream': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['stream'],
            'level': 'ERROR',
            'propagate': True,
        },
        'badgify': {
            'handlers': ['stream'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

if django.VERSION < (1, 6):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'
if django.VERSION < (1, 7):
    SOUTH_MIGRATION_MODULES = {'badgify': 'badgify.south_migrations'}
    INSTALLED_APPS.append('south')
