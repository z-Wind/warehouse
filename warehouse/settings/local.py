"""
Local Develope User

Django settings for warehouse project.

Generated by 'django-admin startproject' using Django 1.8.5.
"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yrr$6%8md1a7m)0^&snj(sv+ch)z)se2v@@kc)w=))z*h^s(yu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
