from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from visitor_tracker.models import Visitor
from .serializers import VisitorSerializer
from visitor_tracker.utils.validators import is_valid_uuid
from django.shortcuts import get_object_or_404
# from drf_yasg.utils from swagger_auto_schema

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
            visitorFound = VisitorSerializer(visitor)
            return Response(visitorFound.data)
        elif request.method == 'DELETE':
            visitor.delete()
            return Response({"succes": "Visitor deleted succesfuly"}, status=status.HTTP_204_NO_CONTENT)
