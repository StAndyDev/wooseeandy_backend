import json, uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Visitor, VisitInfo
from channels.db import database_sync_to_async
from django.utils import timezone
from visitor_tracker.utils.validators import is_valid_uuid
from visitor_tracker.utils.duration_utils import timedelta_to_iso8601
from django.core.cache import cache

PORTFOLIO_TOKEN = "d4f8a1b3c6e9f2g7h0j5k8l2m9n3p4q"
WOOSEEANDY_TOKEN = "a3b7e8f9c2d4g5h6j0k1l2m3n9p8q7r"

class VisitorTrackerConsumer(AsyncWebsocketConsumer):

    list_returning_visitors = []
    list_new_visitors = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visitor_uuid = None
        self.room_name = None
        self.wooseeandy_id = ""
        self.alert_returning_visitor = ""
        self.alert_new_visitor = ""
        self.alert_disconnected_visitor = ""
        self.visit_start_datetime = None
        self.visit_end_datetime = None
    
    # ======================== CONNECT =============================
    async def connect(self):
        query_string = self.scope["query_string"].decode() # get query string
        token = None
        if "token=" in query_string:
            token = query_string.split("token=")[1] # get token
        # portfolio connexion
        if token == PORTFOLIO_TOKEN:
            self.room_name = f"user_{token}"
            await self.channel_layer.group_add(
                self.room_name, self.channel_name
            )
            await self.accept()
            print("----------- CONNEXION VENANT DU PORTFOLIO ETABLIE -----------")
        # wooseeadndy connexion
        elif token == WOOSEEANDY_TOKEN:
            self.room_name = f"user_{token}"
            self.wooseeandy_id = f"user_{uuid.uuid4()}" # créer un uuid pour chaque connexion
            await self.channel_layer.group_add(
                self.room_name, self.channel_name
            )
            await self.channel_layer.group_add(
                self.wooseeandy_id, self.channel_name
            )
            await self.accept()
            print("----------- CONNEXION VENANT DE WOOSEEANDY ETABLIE -----------")
            is_cache_empty = not VisitorTrackerConsumer.list_returning_visitors or not VisitorTrackerConsumer.list_new_visitors
            if not is_cache_empty:
                print("Le cache est vide, il n'y a pas de message à envoyer.")
            else:
                print("Le cache n'est pas vide, il y a des messages à envoyer.")
                # Récupérer les messages du cache
                list_visitors = VisitorTrackerConsumer.list_returning_visitors + VisitorTrackerConsumer.list_new_visitors
                list_visitors = list(set(list_visitors))
                print(f"*****************list_visitors*************** : {list_visitors}")
                for val in list_visitors:
                    messages = cache.get(val)
                    if messages:
                        for message in messages:
                            # Diffuser le message au room du portfolio
                            await self.channel_layer.group_send(
                                self.wooseeandy_id,
                                message
                            )
        else:
            # Fermer la connexion si le token est invalide
            print("-------- connexion fermé --------")
            await self.close()
    
    # ====================== DISCONNECT ========================
    async def disconnect(self, close_code):
        # DECONNECTION DU PORTFOLIO
        if self.room_name == f"user_{PORTFOLIO_TOKEN}":
            visitor_uuid = self.visitor_uuid
            visit_info_uuid = self.scope.get('visit_info_uuid')
            if visit_info_uuid:
                self.visit_end_datetime = timezone.now()
                # Mettre à jour la visite dans la base de données
                await self.update_visit_info(visit_info_uuid, self.visit_end_datetime)
                self.alert_disconnected_visitor = f"Visiteur {visitor_uuid} déconnecté."
                if visitor_uuid in VisitorTrackerConsumer.list_returning_visitors :
                    VisitorTrackerConsumer.list_returning_visitors.remove(visitor_uuid)
                elif visitor_uuid in VisitorTrackerConsumer.list_new_visitors :
                    VisitorTrackerConsumer.list_new_visitors.remove(visitor_uuid)
                print(self.alert_disconnected_visitor)
            else:
                print("Visiteur non identifié déconnecté.")

            await self.channel_layer.group_send(
                f"user_{WOOSEEANDY_TOKEN}",
                {
                    'type': 'disconnect_alert_sender', # appel la méthode disconnect_alert_sender
                    'is_new_visitor': True if visitor_uuid in VisitorTrackerConsumer.list_new_visitors else False,
                    'visit_info_uuid': str(visit_info_uuid),
                    'end_datetime': self.visit_end_datetime.isoformat() if self.visit_end_datetime else None,
                    'visit_duration': timedelta_to_iso8601(self.visit_end_datetime - self.visit_start_datetime) if self.visit_start_datetime and self.visit_end_datetime else None,
                }
            )

            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name
            )
            # vider le cache
            if cache.get(visitor_uuid):
                cache.delete(visitor_uuid)

        # DECONNECTION DE L'APP WOOSEEANDY
        elif self.room_name == f"user_{WOOSEEANDY_TOKEN}":
            await self.channel_layer.group_discard(
                self.wooseeandy_id,
                self.channel_name
            )
            print("wooseeandy app disconnected")
    
    # _______________RECEIVE FROM PORTFOLIO________________
    async def receive_from_portfolio(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json['data']
        # ********************* DATA : VISITOR-INFOS ************************
        # verification de type de message | le visiteur n'est pas encore connecté
        if data.get("type") == "visitor-infos" :
            if data.get("uuidExists") and data["uuidExists"] != "undefined" and is_valid_uuid(data["uuidExists"]) == True:
                visitor_uuid = data["uuidExists"]
                id_exists = await self.check_visitor_exists(visitor_uuid)
                if (not id_exists):
                    await self.save_visitor(id_visitor = visitor_uuid ,navigator_info = data["navigator_info"], os = data["os"], device_type = data["device_type"])
                self.visitor_uuid = visitor_uuid # différent scope pour chaque visiteur
                self.alert_returning_visitor = f"Le visiteur {visitor_uuid} est revenu consulter votre portfolio."
                VisitorTrackerConsumer.list_returning_visitors.append(visitor_uuid)
                print(self.alert_returning_visitor)
                # time of visit
                self.visit_start_datetime = timezone.now()
                # # save visit info
                visit_info_uuid = uuid.uuid4()
                self.scope['visit_info_uuid'] = visit_info_uuid
                await self.save_visit_info(
                    id_visit_info = visit_info_uuid,
                    visitor = visitor_uuid,
                    ip_address = data["ip_address"],
                    location_approx = data["location_approx"],
                    visit_start_datetime = self.visit_start_datetime,
                )
            else:
                visitor_uuid = uuid.uuid4()
                self.visitor_uuid = visitor_uuid
                self.alert_new_visitor = f"Un nouveau visiteur {visitor_uuid} consulte votre portfolio."
                VisitorTrackerConsumer.list_new_visitors.append(visitor_uuid)
                print(self.alert_new_visitor)
                # save visitor
                await self.save_visitor(id_visitor = visitor_uuid ,navigator_info = data["navigator_info"], os = data["os"], device_type = data["device_type"])
                # time of visit
                self.visit_start_datetime = timezone.now()
                # save visit info
                visit_info_uuid = uuid.uuid4()
                self.scope['visit_info_uuid'] = visit_info_uuid
                await self.save_visit_info(
                    id_visit_info = visit_info_uuid,
                    visitor = visitor_uuid,
                    ip_address = data["ip_address"],
                    location_approx = data["location_approx"],
                    visit_start_datetime = self.visit_start_datetime,
                )

            # Diffuser le message au room du portfolio
            await self.channel_layer.group_send(
                f"user_{PORTFOLIO_TOKEN}",
                {
                    'type': 'uuid_sender',
                    'uuid': str(visitor_uuid),
                }
            )
            message_data = {
                    'type': 'connexion_alert_sender',
                    'uuid': str(visitor_uuid),
                    'visit_info_uuid': str(visit_info_uuid),
                    'returning_visitor': self.alert_returning_visitor,
                    'new_visitor': self.alert_new_visitor,
                    'visit_start_datetime': self.visit_start_datetime.isoformat() if self.visit_start_datetime else None,
                    'navigator_info': data["navigator_info"],
                    'os': data["os"],
                    'device_type': data["device_type"],
                    'ip_address': data["ip_address"],
                    'location_approx': data["location_approx"],
                }
            # Diffuser le message à l'app wooseeandy
            await self.channel_layer.group_send(
                f"user_{WOOSEEANDY_TOKEN}",
                message_data
            )
            # mis en cache du message
            mes = cache.get(visitor_uuid, [])
            mes.append(message_data)
            cache.set(visitor_uuid, mes, timeout=3600) # 1h


    # _______________RECEIVE FROM WOOSEEANDY________________
    async def receive_from_wooseeandy(self, text_data):
        text_data_json = json.loads(text_data)
        # data = text_data_json['data']
        # print(f"ITO EEEEEEEE {data}")
    
    
    # ________________RECEIVE___________________
    async def receive(self, text_data):
        if self.room_name == f"user_{PORTFOLIO_TOKEN}":
            await self.receive_from_portfolio(text_data)
        elif self.room_name == f"user_{WOOSEEANDY_TOKEN}":
            await self.receive_from_wooseeandy(text_data)
    
    # this focntion combine uuid_sender and connexion_alert_sender
    # async def combined_sender(self, event):
    #         await self.connexion_alert_sender(event)
    #         await self.uuid_sender(event)

    # Cette méthode est appelée lorsqu'un message est reçu du groupe ,Envoyer le message à l'élément WebSocket
    async def uuid_sender(self, event):
        id = event['uuid']
        await self.send(text_data=json.dumps({
            'uuid': id,
        }))

    async def connexion_alert_sender(self, event):
        visitor_uuid = event['uuid']
        visit_info_uuid = event['visit_info_uuid']
        returning_visitor = event['returning_visitor']
        new_visitor = event['new_visitor']
        visit_start_datetime = event['visit_start_datetime']
        navigator_info = event['navigator_info']
        os = event['os']
        device_type = event['device_type']
        ip_address = event['ip_address']
        location_approx = event['location_approx']

        await self.send(text_data=json.dumps({
            'alert_type': 'connected_alert',  # ceci permet de distinguer les types d'alerte en wooseeandy app
            'visitor_uuid': visitor_uuid,
            'visit_info_uuid': visit_info_uuid,
            'alert_returning_visitor': returning_visitor,
            'alert_new_visitor': new_visitor,
            'visit_start_datetime': visit_start_datetime,
            'navigator_info': navigator_info,
            'os': os,
            'device_type': device_type,
            'ip_address': ip_address,
            'location_approx': location_approx,
        }))
    async def disconnect_alert_sender(self, event):
        is_new_visitor = event['is_new_visitor'] # bool, permet de savoir si le visiteur déconnecté est un nouveau ou pas
        end_datetime = event['end_datetime']
        id_visit_info = event['visit_info_uuid']
        visit_duration = event['visit_duration']
        await self.send(text_data=json.dumps({
            'alert_type': 'disconnected_alert',  # ceci permet de distinguer les types d'alerte en wooseeandy app
            'is_new_visitor': is_new_visitor,
            'visit_info_uuid': id_visit_info,
            'visit_end_datetime': end_datetime,
            'visit_duration': visit_duration,
        }))
    
    # une fonction synchrone pour vérifier l'existence du visiteur
    @database_sync_to_async
    def check_visitor_exists(self, visitor_uuid):
        return Visitor.objects.filter(id_visitor = visitor_uuid).exists()
    
    @database_sync_to_async
    def save_visitor(self, id_visitor, navigator_info, os, device_type):
        return Visitor.objects.create(
            id_visitor = id_visitor,
            navigator_info = navigator_info,
            os = os,
            device_type = device_type
        )
    
    @database_sync_to_async
    def save_visit_info(self, id_visit_info, visitor, ip_address, location_approx, visit_start_datetime):
        visitor_instance = Visitor.objects.get(id_visitor=visitor) # get id
        return VisitInfo.objects.create(
            id_visit_info = id_visit_info,
            visitor = visitor_instance,
            ip_address = ip_address,
            location_approx = location_approx,
            visit_start_datetime = visit_start_datetime,
        )
    
    @database_sync_to_async
    def update_visit_info(self, visit_info_uuid, disconnected_at):
        visit_info = VisitInfo.objects.filter(id_visit_info = visit_info_uuid).last()
        if visit_info:
            visit_info.visit_end_datetime = disconnected_at
            visit_info.visit_duration = disconnected_at - visit_info.visit_start_datetime
            visit_info.save()
            print("date connexion : ", visit_info.visit_start_datetime)
            print("date deconnexion : ", disconnected_at)
            print("Durée de la visite : ", visit_info.visit_duration)