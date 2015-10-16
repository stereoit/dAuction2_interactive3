# -*- coding: utf-8 -*-
"""
Use this template for your local.py settings.
"""
from .base import TEMPLATES

DEBUG=True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dauction2',
        'USER': 'dauction',
        'PASSWORD': 'dauction',
        'HOST': '127.0.0.1'
    }
}


#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': 'db.sqlite',
#    }
#}
