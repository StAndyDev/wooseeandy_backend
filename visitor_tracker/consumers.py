import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from channels.db import database_sync_to_async

class VisitorTrackerConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = "chat_group"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Sauvegarder le message dans la base de données
        await self.save_message(message)

        # Diffuser le message à tous les WebSockets connectés
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
    # Cette méthode est appelée lorsqu'un message est reçu du groupe.
    # Envoyer le message à l'élément WebSocket
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
    
    @database_sync_to_async
    def save_message(self, mes):
        return Message.objects.create(message = mes) # message est le champ de la table Message