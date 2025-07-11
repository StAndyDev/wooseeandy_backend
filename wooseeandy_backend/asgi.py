"""
ASGI config for wooseeandy_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Définit les settings de prod
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wooseeandy_backend.settings.prod')

# Initialise Django (important avant d'importer des modèles)
django_asgi_app = get_asgi_application()

# Import après initialisation de Django
from visitor_tracker.routing import websocket_urlpatterns

# Routeur ASGI
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})