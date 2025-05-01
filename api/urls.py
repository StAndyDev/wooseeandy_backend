from django.urls import path
from .views import VisitorInfoList

urlpatterns = [
    path('visitors-infos/', VisitorInfoList.as_view()),
]