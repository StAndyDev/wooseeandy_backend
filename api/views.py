from visitor_tracker.models import VisitInfo, CVDownload, PortfolioDetailView, Visitor
from .serializers import VisitInfoSerializer, CVDownloadSerializer, PortfolioDetailsViewSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from drf_yasg.utils from swagger_auto_schema
from rest_framework.generics import ListAPIView # pour la liste paginée

from django.utils.timezone import now
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Count
from django.db.models.functions import TruncWeek, TruncMonth

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

# -------- Count VISITINFO, CVDOWNLOAD, PORTFOLIODETAILVIEW -----------
class CountNotification(APIView):
    def get(self, request, *args, **kwargs):
        is_read_param = request.GET.get('is_read')
        # Par défaut, pas de filtrage (on compte tout)
        filter_kwargs = {}

        if is_read_param is not None:
            if is_read_param.lower() == 'true':
                filter_kwargs['is_read'] = True
            elif is_read_param.lower() == 'false':
                filter_kwargs['is_read'] = False
            else:
                return Response({'error': "Paramètre 'is_read' invalide. Utilisez 'true' ou 'false'."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Application du filtre si défini
        visitinfo_count = VisitInfo.objects.filter(**filter_kwargs).count()
        cvdownload_count = CVDownload.objects.filter(**filter_kwargs).count()
        portfoliodetailview_count = PortfolioDetailView.objects.filter(**filter_kwargs).count()

        return Response({
            "visitinfo_count": visitinfo_count,
            "cvdownload_count": cvdownload_count,
            "portfoliodetailview_count": portfoliodetailview_count
        }, status=status.HTTP_200_OK)

# --------------- COUNTER ---------------
class CountVisitor(APIView):
    def get(self, request, *args, **kwargs):
        visitor_count = Visitor.objects.count()
        return Response({
            "visitor_count" : visitor_count
        }, status=status.HTTP_200_OK)

class CountCvDownload(APIView):
    def get(self, request, *args, **kwargs):
        cv_download_count = CVDownload.objects.count()
        return Response({
            "cv_download_count" : cv_download_count
        }, status = status.HTTP_200_OK)

class CountPortfolioDetailsView(APIView):
    def get(self, request, *args, **kwargs):
        portfolio_details_view_count = PortfolioDetailView.objects.count()
        return Response({
            "portfolio_details_view_count" : portfolio_details_view_count
        }, status = status.HTTP_200_OK)
    
# -------------- Nbr Monthly --------------

class MonthlyVisitInfoStatsView(APIView):
    def get(self, request):
        today = now().date()

        # Période actuelle (mois en cours)
        start_current_month = today.replace(day=1)
        end_current_month = (start_current_month + relativedelta(months=1)) - timedelta(seconds=1)

        # Période précédente (mois dernier)
        start_last_month = start_current_month - relativedelta(months=1)
        end_last_month = start_current_month - timedelta(seconds=1)

        # Comptage
        visits_current = VisitInfo.objects.filter(
            visit_start_datetime__date__gte=start_current_month,
            visit_start_datetime__date__lte=end_current_month
        ).count()

        visits_last = VisitInfo.objects.filter(
            visit_start_datetime__date__gte=start_last_month,
            visit_start_datetime__date__lte=end_last_month
        ).count()

        # Calcul de la variation | j'aimerai calculer la variation côté client
        # if visits_last > 0:
        #     change = ((visits_current - visits_last) / visits_last) * 100
        # else:
        #     change = 0.0 if visits_current == 0 else 100.0  # Si aucun visite le mois dernier
        # arrondissement
        # "change_percentage": round(change, 2)

        return Response({
            "current_month": visits_current,
            "last_month": visits_last,
        })


class MonthlyPortfolioDetailViewStatsView(APIView):
    def get(self, request):
        today = now().date()

        # Définir les bornes du mois actuel
        start_current_month = today.replace(day=1)
        end_current_month = (start_current_month + relativedelta(months=1)) - timedelta(seconds=1)

        # Définir les bornes du mois précédent
        start_last_month = start_current_month - relativedelta(months=1)
        end_last_month = start_current_month - timedelta(seconds=1)

        # Compter les vues
        current_month_views = PortfolioDetailView.objects.filter(
            view_datetime__date__gte=start_current_month,
            view_datetime__date__lte=end_current_month
        ).count()

        last_month_views = PortfolioDetailView.objects.filter(
            view_datetime__date__gte=start_last_month,
            view_datetime__date__lte=end_last_month
        ).count()

        return Response({
            "current_month": current_month_views,
            "last_month": last_month_views,
        })

class MonthlyCVDownloadStatsView(APIView):
    def get(self, request):
        today = now().date()

        # Mois actuel
        start_current_month = today.replace(day=1)
        end_current_month = (start_current_month + relativedelta(months=1)) - timedelta(seconds=1)

        # Mois précédent
        start_last_month = start_current_month - relativedelta(months=1)
        end_last_month = start_current_month - timedelta(seconds=1)

        # Nombre de téléchargements
        downloads_current = CVDownload.objects.filter(
            download_datetime__date__gte=start_current_month,
            download_datetime__date__lte=end_current_month
        ).count()

        downloads_last = CVDownload.objects.filter(
            download_datetime__date__gte=start_last_month,
            download_datetime__date__lte=end_last_month
        ).count()

        return Response({
            "current_month": downloads_current,
            "last_month": downloads_last,
        })
    
# -------------- Nbr 7 last Month/Week --------------

MONTHS_FR = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

class SevenLastVisitInfoStatsView(APIView):
    def get(self, request, *args, **kwargs):
        mode = request.GET.get('mode', 'month')
        today = now()
        queryset = VisitInfo.objects.all()

        if mode == 'week':
            truncate_func = TruncWeek
            start_of_week = today - timedelta(days=today.weekday())
            periods = [start_of_week - timedelta(weeks=i) for i in range(6, -1, -1)]

            annotated = queryset.annotate(
                period=truncate_func('visit_start_datetime')
            ).values('period').annotate(count=Count('id_visit_info'))

            counts = {entry['period'].date(): entry['count'] for entry in annotated}

            labels = [f"S{i+1}" for i in range(7)]
            result = [counts.get(p.date(), 0) for p in periods]

        else:
            truncate_func = TruncMonth
            start_of_month = today.replace(day=1)
            periods = [start_of_month - relativedelta(months=i) for i in range(6, -1, -1)]

            annotated = queryset.annotate(
                period=truncate_func('visit_start_datetime')
            ).values('period').annotate(count=Count('id_visit_info'))

            counts = {entry['period'].date(): entry['count'] for entry in annotated}

            labels = [
                f"{MONTHS_FR[p.month]} {p.year}" for p in periods
            ]
            result = [counts.get(p.date(), 0) for p in periods]

        return Response({
            'labels': labels,
            'visit_info': result
        }, status=status.HTTP_200_OK)
    
class SevenLastCVDownloadStatsView(APIView):
    def get(self, request, *args, **kwargs):
        mode = request.GET.get('mode', 'month')
        today = now()
        queryset = CVDownload.objects.all()

        if mode == 'week':
            truncate_func = TruncWeek
            start_of_week = today - timedelta(days=today.weekday())
            periods = [start_of_week - timedelta(weeks=i) for i in range(6, -1, -1)]

            annotated = queryset.annotate(
                period=truncate_func('download_datetime')
            ).values('period').annotate(count=Count('id_cv_download'))

            counts = {entry['period'].date(): entry['count'] for entry in annotated}

            labels = [f"S{i+1}" for i in range(7)]
            result = [counts.get(p.date(), 0) for p in periods]

        else:
            truncate_func = TruncMonth
            start_of_month = today.replace(day=1)
            periods = [start_of_month - relativedelta(months=i) for i in range(6, -1, -1)]

            annotated = queryset.annotate(
                period=truncate_func('download_datetime')
            ).values('period').annotate(count=Count('id_cv_download'))

            counts = {entry['period'].date(): entry['count'] for entry in annotated}

            labels = [f"{MONTHS_FR[p.month]} {p.year}" for p in periods]
            result = [counts.get(p.date(), 0) for p in periods]

        return Response({
            'labels': labels,
            'cv_download': result
        }, status=status.HTTP_200_OK)
    

class SevenLastPortfolioDetailViewStatsView(APIView):
    def get(self, request, *args, **kwargs):
        mode = request.GET.get('mode', 'month')
        today = now()
        queryset = PortfolioDetailView.objects.all()

        if mode == 'week':
            truncate_func = TruncWeek
            start_of_week = today - timedelta(days=today.weekday())
            periods = [start_of_week - timedelta(weeks=i) for i in range(6, -1, -1)]

            annotated = queryset.annotate(
                period=truncate_func('view_datetime')
            ).values('period').annotate(count=Count('id_portfolio_detail_view'))

            counts = {entry['period'].date(): entry['count'] for entry in annotated}

            labels = [f"S{i+1}" for i in range(7)]
            result = [counts.get(p.date(), 0) for p in periods]

        else:
            truncate_func = TruncMonth
            start_of_month = today.replace(day=1)
            periods = [start_of_month - relativedelta(months=i) for i in range(6, -1, -1)]

            annotated = queryset.annotate(
                period=truncate_func('view_datetime')
            ).values('period').annotate(count=Count('id_portfolio_detail_view'))

            counts = {entry['period'].date(): entry['count'] for entry in annotated}

            labels = [f"{MONTHS_FR[p.month]} {p.year}" for p in periods]
            result = [counts.get(p.date(), 0) for p in periods]

        return Response({
            'labels': labels,
            'portfolio_detail_view': result
        }, status=status.HTTP_200_OK)
    
