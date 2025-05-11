from visitor_tracker.models import VisitInfo, CVDownload, PortfolioDetailView
from .serializers import VisitInfoSerializer, CVDownloadSerializer, PortfolioDetailsViewSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from drf_yasg.utils from swagger_auto_schema
from rest_framework.generics import ListAPIView # pour la liste paginée

# ------ LIST API VIEW -------
class VisitorInfoList(ListAPIView):
    queryset = VisitInfo.objects.all().order_by('-visit_start_datetime')  # tri du plus récent au plus ancien
    serializer_class = VisitInfoSerializer

class CVDownloadList(ListAPIView):
    queryset = CVDownload.objects.all().order_by('-download_datetime')
    serializer_class = CVDownloadSerializer

class PortfolioDetailsViewList(ListAPIView):
    queryset = PortfolioDetailView.objects.all().order_by('-view_datetime')
    serializer_class = PortfolioDetailsViewSerializer

# ------ MARK AS TRUE API ------
# VisitInfo
class MarkVisitInfoAsRead(APIView):
    def post(self, request, pk, *args, **kwargs):
        try:
            visit_info = VisitInfo.objects.get(pk=pk)
            visit_info.is_read = True
            visit_info.save()
            return Response({"message": "VisitInfo marked as read."}, status=status.HTTP_200_OK)
        except VisitInfo.DoesNotExist:
            return Response({"error": "VisitInfo not found."}, status=status.HTTP_404_NOT_FOUND)
        
# CVDownload
class MarkCVDownloadAsRead(APIView):
    def post(self, request, pk, *args, **kwargs):
        try:
            cv_download = CVDownload.objects.get(pk=pk)
            cv_download.is_read = True
            cv_download.save()
            return Response({"message": "CVDownload marked as read."}, status=status.HTTP_200_OK)
        except CVDownload.DoesNotExist:
            return Response({"error": "CVDownload not found."}, status=status.HTTP_404_NOT_FOUND)
        
# PortfolioDetailView
class MarkPortfolioDetailViewAsRead(APIView):
    def post(self, request, pk, *args, **kwargs):
        try:
            portfolio_detail_view = PortfolioDetailView.objects.get(pk=pk)
            portfolio_detail_view.is_read = True
            portfolio_detail_view.save()
            return Response({"message": "PortfolioDetailView marked as read."}, status=status.HTTP_200_OK)
        except PortfolioDetailView.DoesNotExist:
            return Response({"error": "PortfolioDetailView not found."}, status=status.HTTP_404_NOT_FOUND)

# ------- DELETE API -------
# VisitInfo
class DeleteVisitInfo(APIView):
    def delete(self, request, pk, *args, **kwargs):
        try:
            visit_info = VisitInfo.objects.get(pk=pk)
            visit_info.delete()
            return Response({"message": "VisitInfo deleted."}, status=status.HTTP_200_OK)
        except VisitInfo.DoesNotExist:
            return Response({"error": "VisitInfo not found."}, status=status.HTTP_404_NOT_FOUND)
        
# CVDownload
class DeleteCVDownload(APIView):
    def delete(self, request, pk, *args, **kwargs):
        try:
            cv_download = CVDownload.objects.get(pk=pk)
            cv_download.delete()
            return Response({"message": "CVDownload deleted."}, status=status.HTTP_200_OK)
        except CVDownload.DoesNotExist:
            return Response({"error": "CVDownload not found."}, status=status.HTTP_404_NOT_FOUND)
        
# PortfolioDetailView
class DeletePortfolioDetailView(APIView):
    def delete(self, request, pk, *args, **kwargs):
        try:
            portfolio_detail_view = PortfolioDetailView.objects.get(pk=pk)
            portfolio_detail_view.delete()
            return Response({"message": "PortfolioDetailView deleted."}, status=status.HTTP_200_OK)
        except PortfolioDetailView.DoesNotExist:
            return Response({"error": "PortfolioDetailView not found."}, status=status.HTTP_404_NOT_FOUND)
