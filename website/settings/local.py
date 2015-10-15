# -*- coding: utf-8 -*-
from .base import TEMPLATES

DEBUG=True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

ALLOWED_HOSTS = ['*']

# this goes into production configuration
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'slvstr_db',
#        'USER': 'postgres2',
#        'PASSWORD': 'a',
#        'HOST': '127.0.0.1',
#        'PORT': '9999',
#    }
#}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}
