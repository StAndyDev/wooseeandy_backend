from .base import *
# Utilise la DB fournie par Render via la variable d’env
import dj_database_url
import os

DEBUG = False
# ALLOWED_HOSTS = ['https://wooseeandy-backend.onrender.com/']
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
CORS_ALLOWED_ORIGINS = [
    "https://sitraka-andy.vercel.app",  # ton portfolio
    "exp://*",                          # pour dev avec Expo (mobile)
]

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}
# Static files (Render les sert si tu les collectes dans /staticfiles)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
