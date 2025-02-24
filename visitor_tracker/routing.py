from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/visitor-tracker/', consumers.VisitorTrackerConsumer.as_asgi()),
]