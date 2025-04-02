from django.urls import path
from .views import all_visitors, visitor_by_id, patch_visit_info

urlpatterns = [
    path('visitors/', all_visitors, name='get_all_visitors'),
    path('visitor/<uuid:pk>/', visitor_by_id, name='get_or_delete_specific_visitor'),
    path('visit_info/<int:pk>/patch/', patch_visit_info, name='update-visit_info-patch')
]