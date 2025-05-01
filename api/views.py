from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from visitor_tracker.models import Visitor, VisitInfo
from .serializers import VisitorSerializer, VisitInfoSerializer
from visitor_tracker.utils.validators import is_valid_uuid
from django.shortcuts import get_object_or_404
# from drf_yasg.utils from swagger_auto_schema
from rest_framework.generics import ListAPIView # pour la liste paginée

class VisitorInfoList(ListAPIView):
    # queryset = Visitor.objects.all().order_by('-created_at')  # tri du plus récent au plus ancien
    queryset = VisitInfo.objects.all()
    serializer_class = VisitInfoSerializer


@api_view(['GET'])
def all_visitors(request):
    visitors = Visitor.objects.prefetch_related('visits').all()  # Optimisation
    serializer = VisitorSerializer(visitors, many=True)
    return Response(serializer.data)

@api_view(['GET', 'DELETE'])
def visitor_by_id(request, pk):
    if not is_valid_uuid(pk):
        return Response({"error": "Invalid UUID"}, status=status.HTTP_400_BAD_REQUEST)
    else :
        visitor = get_object_or_404(Visitor, id=pk)
        if request.method == 'GET':
            visitor_found = VisitorSerializer(visitor)
            return Response(visitor_found.data)
        elif request.method == 'DELETE':
            visitor.delete()
            return Response({"succes": "Visitor deleted succesfuly"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['PATCH'])
def patch_visit_info(request, pk):
    try:
        visit_info = VisitInfo.objects.get(pk=pk)
    except VisitInfo.DoesNotExist:
        return Response({"error": "Visit info not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = VisitorSerializer(visit_info, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
