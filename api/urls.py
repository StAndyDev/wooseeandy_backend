from django.urls import path
from .views import (
    VisitorInfoList,
    CVDownloadList,
    PortfolioDetailsViewList,
    MarkVisitInfoAsRead,
    MarkCVDownloadAsRead,
    MarkPortfolioDetailViewAsRead,
    DeleteVisitInfo,
    DeleteCVDownload,
    DeletePortfolioDetailView,
    CountNotification,
    CountVisitor,
    CountCvDownload,
    CountPortfolioDetailsView,
    MonthlyVisitInfoStatsView,
    MonthlyPortfolioDetailViewStatsView,
    MonthlyCVDownloadStatsView,
    SevenLastVisitInfoStatsView,
    SevenLastCVDownloadStatsView,
    SevenLastPortfolioDetailViewStatsView,
    BrowserStatsAPIView,
    PingView,
    SaveWooseeandyUserTokenView
)

urlpatterns = [
    path('visitors-infos-list/', VisitorInfoList.as_view()),
    path('cv-downloads-list/', CVDownloadList.as_view()),
    path('portfolio-details-view-list/', PortfolioDetailsViewList.as_view()),
    path('mark-visit-info-as-read/<str:pk>/', MarkVisitInfoAsRead.as_view()),
    path('mark-cv-download-as-read/<str:pk>/', MarkCVDownloadAsRead.as_view()),
    path('mark-portfolio-detail-view-as-read/<str:pk>/', MarkPortfolioDetailViewAsRead.as_view()),
    path('delete-visit-info/<uuid:pk>/', DeleteVisitInfo.as_view()),
    path('delete-cv-download/<uuid:pk>/', DeleteCVDownload.as_view()),
    path('delete-portfolio-detail-view/<uuid:pk>/', DeletePortfolioDetailView.as_view()),
    path('notifications/count/', CountNotification.as_view()),
    path('visitor/count/', CountVisitor.as_view()),
    path('cv-download/count/', CountCvDownload.as_view()),
    path('portfolio-details-view/count/', CountPortfolioDetailsView.as_view()),
    path('visit-info-stats/monthly/', MonthlyVisitInfoStatsView.as_view()),
    path('portfolio-detail-stats/monthly/', MonthlyPortfolioDetailViewStatsView.as_view()),
    path('cv-download-stats/monthly/', MonthlyCVDownloadStatsView.as_view()),
    path('seven-last-visit-info/stats/', SevenLastVisitInfoStatsView.as_view()),
    path('seven-last-cv-download/stats/', SevenLastCVDownloadStatsView.as_view()),
    path('seven-last-portfolio-detail/stats/', SevenLastPortfolioDetailViewStatsView.as_view()),
    path('browser-stats/', BrowserStatsAPIView.as_view()),
    path('ping/', PingView.as_view()), # ping
    path('save-wooseeandy-user-token', SaveWooseeandyUserTokenView.as_view()),
]