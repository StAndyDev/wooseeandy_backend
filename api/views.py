from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from visitor_tracker.models import Visitor
from .serializers import VisitorSerializer
# from drf_yasg.utils from swagger_auto_schema

@api_view(['GET'])
def all_visitors(request):
    visitors = Visitor.objects.all()
    serializer = VisitorSerializer(visitors, many=True)
    return Response(serializer.data)

@api_view(['GET', 'DELETE'])
def visitor_by_id(request, pk): # il faut vérifier d'abord l'uuid
    try:
        visitor = Visitor.objects.get(id=pk)
    except Visitor.DoesNotExist:
        return Response({"error": "Visitor not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        visitorFound = VisitorSerializer(visitor)
        return Response(visitorFound.data)
    elif request.method == 'DELETE':
        visitor.delete()
        return Response({"succes": "Visitor deleted succesfuly"}, status=status.HTTP_201_CREATED)
