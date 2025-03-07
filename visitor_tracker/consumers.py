import json, uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, Visitor, VisitInfo
from channels.db import database_sync_to_async
from django.utils import timezone

class VisitorTrackerConsumer(AsyncWebsocketConsumer):
    # CONNECT
    async def connect(self):
        self.group_name = "live_visitors"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name # Identifiant unique du canal du client
        )
        await self.accept()
    
    # DISCONNECT
    async def disconnect(self, close_code):
        visitor_uuid = self.scope.get('visitor_uuid')
        if visitor_uuid:
            self.visit_end_datetime = timezone.now()
            # Mettre à jour la visite dans la base de données
            await self.update_visit_info(visitor_uuid, self.visit_end_datetime)
            print(f"Visiteur {visitor_uuid} déconnecté.")
        else:
            print("Visiteur non identifié déconnecté.")
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    # RECEIVE
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json['data']

        # verification de l'existence de l'uuid (qui vient du côté client)
        if(data["uuidExists"]) :
            print("uuidExists en LOCAL")
            visitor_uuid = data["uuidExists"]
            id_exists = await self.check_visitor_exists(visitor_uuid)
            print(f"UUID TROUVEEEEEEEEEEEEEEEEEEEEEE ANATY BASE? {(id_exists)}")

            if (not id_exists):
                print ("ANATY NOT EXISTS ANATY BASE")
                await self.save_visitor(id = visitor_uuid ,navigator_info = data["navigator_info"], os = data["os"], device_type = data["device_type"])
            
            self.scope['visitor_uuid'] = visitor_uuid # stocker l'uuid dans le scope du consumer
            print(f"Le visiteur {visitor_uuid} est revenu consulter votre portfolio.")
            # time of visit
            self.start_datetime = timezone.now()
            # # save visit info
            await self.save_visit_info(
                visitor = visitor_uuid,
                ip_address = data["ip_address"],
                location_approx = data["location_approx"],
                visit_start_datetime = self.start_datetime,
            )
        else:
            print("uuid not exists")
            visitor_uuid = uuid.uuid4()
            self.scope['visitor_uuid'] = visitor_uuid
            print(f"Un nouveau visiteur {visitor_uuid} consulte votre portfolio.")
            # save visitor
            await self.save_visitor(id = visitor_uuid ,navigator_info = data["navigator_info"], os = data["os"], device_type = data["device_type"])
            # time of visit
            self.start_datetime = timezone.now()
            # save visit info
            await self.save_visit_info(
                visitor = visitor_uuid,
                ip_address = data["ip_address"],
                location_approx = data["location_approx"],
                visit_start_datetime = self.start_datetime,
            )
        # Diffuser le message à tous les WebSockets connectés
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'uuid_sender', # appel la méthode uuid_sender
                'uuid': str(visitor_uuid)
            }
        )

    # Cette méthode est appelée lorsqu'un message est reçu du groupe ,Envoyer le message à l'élément WebSocket
    async def uuid_sender(self, event):
        id = event['uuid']
        await self.send(text_data=json.dumps({
            'uuid': id
        }))
    
    # une fonction synchrone pour vérifier l'existence du visiteur
    @database_sync_to_async
    def check_visitor_exists(self, visitor_uuid):
        return Visitor.objects.filter(id = visitor_uuid).exists()

    @database_sync_to_async
    def save_message(self, mes):
        return Message.objects.create(message = mes) # message est le champ de la table Message
    
    @database_sync_to_async
    def save_visitor(self, id, navigator_info, os, device_type):
        return Visitor.objects.create(
            id = id,
            navigator_info = navigator_info,
            os = os,
            device_type = device_type
        )
    
    @database_sync_to_async
    def save_visit_info(self, visitor, ip_address, location_approx, visit_start_datetime):
        visitor_instance = Visitor.objects.get(id=visitor) # get id
        return VisitInfo.objects.create(
            visitor = visitor_instance,
            ip_address = ip_address,
            location_approx = location_approx,
            visit_start_datetime = visit_start_datetime,
        )
    
    @database_sync_to_async
    def update_visit_info(self, visitor_uuid, disconnected_at):
        visit_info = VisitInfo.objects.filter(visitor = visitor_uuid).last()
        if visit_info:
            visit_info.visit_end_datetime = disconnected_at
            visit_info.visit_duration = disconnected_at - visit_info.visit_start_datetime
            visit_info.save()
            print("date connexion : ", visit_info.visit_start_datetime)
            print("date deconnexion : ", disconnected_at)
            print("Durée de la visite : ", visit_info.visit_duration)