from django.urls import path
from .views import get_all_messages

urlpatterns = [
    path('messages/', get_all_messages, name='get_all_messages'),
]