import json, uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Visitor, VisitInfo
from channels.db import database_sync_to_async
from django.utils import timezone
from visitor_tracker.utils.validators import is_valid_uuid

PORTFOLIO_TOKEN = "d4f8a1b3c6e9f2g7h0j5k8l2m9n3p4q"
WOOSEEANDY_TOKEN = "a3b7e8f9c2d4g5h6j0k1l2m3n9p8q7r"

class VisitorTrackerConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = "live_visitors"
        self.room_name = None
        self.alert_returning_visitor = ""
        self.alert_new_visitor = ""
        self.alert_disconnected_visitor = ""
        self.start_datetime = None
        self.visit_end_datetime = None
    
    # _______________RECEIVE FROM PORTFOLIO________________
    async def receive_from_portfolio(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json['data']
        # verification de l'existence de l'uuid (qui vient du côté client)
        if data.get("uuidExists") and data["uuidExists"] != "undefined" and is_valid_uuid(data["uuidExists"]) == True :
            visitor_uuid = data["uuidExists"]
            id_exists = await self.check_visitor_exists(visitor_uuid)
            if (not id_exists):
                await self.save_visitor(id = visitor_uuid ,navigator_info = data["navigator_info"], os = data["os"], device_type = data["device_type"])
            
            self.scope['visitor_uuid'] = visitor_uuid # stocker l'uuid dans le scope du consumer
            self.alert_returning_visitor = f"Le visiteur {visitor_uuid} est revenu consulter votre portfolio."
            print(self.alert_returning_visitor)
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
            visitor_uuid = uuid.uuid4()
            self.scope['visitor_uuid'] = visitor_uuid
            self.alert_new_visitor = f"Un nouveau visiteur {visitor_uuid} consulte votre portfolio."
            print(self.alert_new_visitor)
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
        # Diffuser le message à tous les rooms WebSockets connectés
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'uuid_sender',
                'uuid': str(visitor_uuid),
            }
        )

    # _______________RECEIVE FROM WOOSEEANDY________________
    async def receive_from_wooseeandy(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json['data']
        print(f"ITO EEEEEEEE {data}")
        # verification de l'existence de l'uuid (qui vient du côté client)
        if data.get("uuidExists") and data["uuidExists"] != "undefined" and is_valid_uuid(data["uuidExists"]) == True :
            visitor_uuid = data["uuidExists"]
            id_exists = await self.check_visitor_exists(visitor_uuid)
            if (not id_exists):
                await self.save_visitor(id = visitor_uuid ,navigator_info = data["navigator_info"], os = data["os"], device_type = data["device_type"])
            
            self.scope['visitor_uuid'] = visitor_uuid # stocker l'uuid dans le scope du consumer
            self.alert_returning_visitor = f"Le visiteur {visitor_uuid} est revenu consulter votre portfolio."
            print(self.alert_returning_visitor)
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
            visitor_uuid = uuid.uuid4()
            self.scope['visitor_uuid'] = visitor_uuid
            self.alert_new_visitor = f"Un nouveau visiteur {visitor_uuid} consulte votre portfolio."
            print(self.alert_new_visitor)
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
            self.room_name,
            {
                'type': 'combined_sender',
                'returning_visitor': self.alert_returning_visitor,
                'new_visitor': self.alert_new_visitor,
                'start_datetime': self.start_datetime.strftime("%Y-%m-%d %H:%M:%S") if self.start_datetime else None ,
                'disconnected_visitor': self.alert_disconnected_visitor,
                'end_datetime': self.visit_end_datetime.strftime("%Y-%m-%d %H:%M:%S") if self.visit_end_datetime else None,
                'uuid': str(visitor_uuid),
            }
        )
    
    # _______________CONNECT_________________
    async def connect(self):
        query_string = self.scope["query_string"].decode() # get query string
        token = None
        if "token=" in query_string:
            token = query_string.split("token=")[1] # get token
            print(f"TOKEN______ {token}")
        if token in [PORTFOLIO_TOKEN, WOOSEEANDY_TOKEN]:
            self.room_name = f"user_{token}"  # Identifiant unique basé sur le token
            await self.channel_layer.group_add(
                self.room_name, self.channel_name
            )
            await self.accept()
            print("_______________Connexion établie_____________.")
        else:
            # Fermer la connexion si le token est invalide
            await self.close()

    
    # _________________DISCONNECT________________
    async def disconnect(self, close_code):
        visitor_uuid = self.scope.get('visitor_uuid')
        if visitor_uuid:
            self.visit_end_datetime = timezone.now()
            # Mettre à jour la visite dans la base de données
            await self.update_visit_info(visitor_uuid, self.visit_end_datetime)
            self.alert_disconnected_visitor = f"Visiteur {visitor_uuid} déconnecté."
            print(self.alert_disconnected_visitor)
        else:
            print("Visiteur non identifié déconnecté.")

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'disconnect_alert_sender', # appel la méthode disconnect_alert_sender
                'disconnected_visitor': self.alert_disconnected_visitor,
                'end_datetime': self.visit_end_datetime.strftime("%Y-%m-%d %H:%M:%S") if self.visit_end_datetime else None,
            }
        )

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    # ________________RECEIVE___________________
    async def receive(self, text_data):
        if self.room_name == "user_d4f8a1b3c6e9f2g7h0j5k8l2m9n3p4q":
            self.receive_from_portfolio(text_data)
            print("______________FROM_PORTFOLIO___________")
        elif self.room_name == "user_a3b7e8f9c2d4g5h6j0k1l2m3n9p8q7r":
            self.receive_from_wooseeandy(text_data)
            print("______________FROM_WOOSEEANDY___________")
    
    # this focntion combine uuid_sender and connexion_alert_sender
    async def combined_sender(self, event):
            await self.connexion_alert_sender(event)
            await self.uuid_sender(event)

    # Cette méthode est appelée lorsqu'un message est reçu du groupe ,Envoyer le message à l'élément WebSocket
    async def uuid_sender(self, event):
        id = event['uuid']
        await self.send(text_data=json.dumps({
            'uuid': id,
        }))

    async def connexion_alert_sender(self, event):
        returning_visitor = event['returning_visitor']
        new_visitor = event['new_visitor']
        start_datetime = event['start_datetime']
        await self.send(text_data=json.dumps({
            'alert_returning_visitor': returning_visitor,
            'alert_new_visitor': new_visitor,
            'visit_start_datetime': start_datetime ,
        }))
    async def disconnect_alert_sender(self, event):
        disconnected_visitor = event['disconnected_visitor']
        end_datetime = event['end_datetime']
        await self.send(text_data=json.dumps({
            'alert_disconnected_visitor': disconnected_visitor,
            'visit_end_datetime': end_datetime,
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