from django.urls import path
from .views import VisitorInfoList, CVDownloadList, PortfolioDetailsViewList, MarkVisitInfoAsRead, MarkCVDownloadAsRead, MarkPortfolioDetailViewAsRead

urlpatterns = [
    path('visitors-infos-list/', VisitorInfoList.as_view()),
    path('cv-downloads-list/', CVDownloadList.as_view()),
    path('portfolio-details-view-list/', PortfolioDetailsViewList.as_view()),
    path('mark-visit-info-as-read/<str:pk>/', MarkVisitInfoAsRead.as_view()),
    path('mark-cv-download-as-read/<str:pk>/', MarkCVDownloadAsRead.as_view()),
    path('mark-portfolio-detail-view-as-read/<str:pk>/', MarkPortfolioDetailViewAsRead.as_view()),
]