from rest_framework.decorators import api_view
from rest_framework.response import Response
from visitor_tracker.models import Message
from .serializers import MessageSerializer

@api_view(['GET'])
def get_all_messages(request):
    messages = Message.objects.all()  # Récupère tous les messages
    serializer = MessageSerializer(messages, many=True)  # Sérialisation
    return Response(serializer.data)  # Retourne les données au format JSON