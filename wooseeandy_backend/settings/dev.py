from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8081',
    "http://localhost:19000",  # Port de Metro Bundler (Expo)
    "http://192.168.137.1:8000",
]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'visitor_tracker',
        'USER': 'postgres',
        'PASSWORD': 'andyandy',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}