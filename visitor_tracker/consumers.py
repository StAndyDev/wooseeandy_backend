import json, uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Visitor, VisitInfo, CVDownload, PortfolioDetailView
from channels.db import database_sync_to_async
from django.utils import timezone
from visitor_tracker.utils.validators import is_valid_uuid
from visitor_tracker.utils.duration_utils import timedelta_to_iso8601
from django.core.cache import cache

PORTFOLIO_TOKEN = "d4f8a1b3c6e9f2g7h0j5k8l2m9n3p4q"
WOOSEEANDY_TOKEN = "a3b7e8f9c2d4g5h6j0k1l2m3n9p8q7r"

class VisitorTrackerConsumer(AsyncWebsocketConsumer):

    list_returning_visitors = []    # list des uuid de Visitor pour envoyer les alertes de deconnexion au wooseeandy
    list_new_visitors = []  # list des uuid de Visitor pour envoyer les alertes de deconnexion au wooseeandy
    list_visit_info = []    # list des uuid de VisitInfo pour utiliser dans le cache
    list_cv_download = []   # list des uuid de CVDownload pour utiliser dans le cache
    list_portfolio_detail_view = [] # list des uuid de PortfolioDetailView  pour utiliser dans le cache

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visitor_uuid = None
        self.room_name = None
        self.wooseeandy_id = "" # variable d'instance pour chaque connection wooseeandy
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
            # Récupérer les uuid du visitInfo dans la liste
            list_visitInfo = list(set( VisitorTrackerConsumer.list_visit_info)) # supprimer les doublons
            for val in list_visitInfo:
                messages = cache.get(f"visit_info_data_{val}")
                if messages:
                    for message in messages:
                        # Diffuser le message au room du portfolio
                        await self.channel_layer.group_send(
                            self.wooseeandy_id,
                            message
                        )
            # Récupérer les uuid du cv_download dans la liste
            list_cv_download = list(set( VisitorTrackerConsumer.list_cv_download)) # supprimer les doublons
            for val in list_cv_download:
                messages = cache.get(f"cv_download_{val}")
                if messages:
                    for message in messages:
                        # Diffuser le message au room du portfolio
                        await self.channel_layer.group_send(
                            self.wooseeandy_id,
                            message
                        )
            # Récupérer les uuid du portfolio_detail_view dans la liste
            list_portfolio_detail_view = list(set( VisitorTrackerConsumer.list_portfolio_detail_view)) # supprimer les doublons
            for val in list_portfolio_detail_view:
                messages = cache.get(f"portfolio_detail_view_{val}")
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
                # supprimer le visitor de la liste des visiteurs
                if visitor_uuid in VisitorTrackerConsumer.list_returning_visitors :
                    VisitorTrackerConsumer.list_returning_visitors.remove(visitor_uuid)
                elif visitor_uuid in VisitorTrackerConsumer.list_new_visitors :
                    VisitorTrackerConsumer.list_new_visitors.remove(visitor_uuid)
                # supprimer le visitInfo de la liste des visitInfo
                if visit_info_uuid in VisitorTrackerConsumer.list_visit_info :
                    VisitorTrackerConsumer.list_visit_info.remove(visit_info_uuid)
                # supprimer le cv_download de la liste des cv_download
                if visit_info_uuid in VisitorTrackerConsumer.list_cv_download :
                    VisitorTrackerConsumer.list_cv_download.remove(visit_info_uuid)
                # supprimer le portfolio_detail_view de la liste des portfolio_detail_view
                if visit_info_uuid in VisitorTrackerConsumer.list_portfolio_detail_view :
                    VisitorTrackerConsumer.list_portfolio_detail_view.remove(visit_info_uuid)
                print(self.alert_disconnected_visitor)
            else:
                print("Visiteur non identifié déconnecté.")

            await self.channel_layer.group_send(
                f"user_{WOOSEEANDY_TOKEN}",
                {
                    'type': 'disconnect_alert_sender', # appel la méthode disconnect_alert_sender
                    'is_new_visitor': True if str(visitor_uuid) in VisitorTrackerConsumer.list_new_visitors else False,
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
            if cache.get(f"visit_info_data_{visitor_uuid}"):
                cache.delete(f"visit_info_data_{visitor_uuid}")
            if cache.get(f"cv_download_{visitor_uuid}"):
                cache.delete(f"cv_download_{visitor_uuid}")
            if cache.get(f"portfolio_detail_view_{visitor_uuid}"):
                cache.delete(f"portfolio_detail_view_{visitor_uuid}")

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
        # ********************* DATA TYPE : VISITOR-INFOS ************************
        # verification de type de message | si le visiteur est récurrent ou pas
        if data.get("type") == "visitor-infos" :
            if data.get("uuidExists") and data["uuidExists"] != "undefined" and is_valid_uuid(data["uuidExists"]) == True:
                visitor_uuid = data["uuidExists"]
                id_exists = await self.check_visitor_exists(visitor_uuid)
                if (not id_exists):
                    await self.save_visitor(id_visitor = visitor_uuid ,navigator_info = data["navigator_info"], os = data["os"], device_type = data["device_type"])
                self.visitor_uuid = visitor_uuid # différent instance pour chaque visiteur
                self.alert_returning_visitor = f"Le visiteur {visitor_uuid} est revenu consulter votre portfolio."
                VisitorTrackerConsumer.list_returning_visitors.append(visitor_uuid)
                print(self.alert_returning_visitor)
                # time of visit
                self.visit_start_datetime = timezone.now()
                # # save visit info
                visit_info_uuid = uuid.uuid4()
                while await self.check_visit_info_exists(visit_info_uuid):
                    visit_info_uuid = uuid.uuid4()
                    print('--inside while loop (check_visit_info_exists)--')
                self.scope['visit_info_uuid'] = visit_info_uuid
                await self.save_visit_info(
                    id_visit_info = visit_info_uuid,
                    visitor = visitor_uuid,
                    ip_address = data["ip_address"],
                    location_approx = data["location_approx"],
                    visit_start_datetime = self.visit_start_datetime,
                )
                # update visitor state in database
                await self.update_visitor_state(visitor_uuid, is_new_visitor = False)
                # mis à jour de la liste des visitInfo
                VisitorTrackerConsumer.list_visit_info.append(visit_info_uuid)
            else:
                visitor_uuid = uuid.uuid4()
                while await self.check_visitor_exists(visitor_uuid):
                    visitor_uuid = uuid.uuid4()
                    print('--inside while loop (check_visitor_exists)--')
                self.visitor_uuid = visitor_uuid
                self.alert_new_visitor = f"Un nouveau visiteur {visitor_uuid} consulte votre portfolio."
                VisitorTrackerConsumer.list_new_visitors.append(str(visitor_uuid))
                print(self.alert_new_visitor)
                # save visitor
                await self.save_visitor(id_visitor = visitor_uuid ,navigator_info = data["navigator_info"], os = data["os"], device_type = data["device_type"])
                # time of visit
                self.visit_start_datetime = timezone.now()
                # save visit info
                visit_info_uuid = uuid.uuid4()
                while await self.check_visit_info_exists(visit_info_uuid):
                    visit_info_uuid = uuid.uuid4()
                    print('--inside while loop (check_visit_info_exists)--')
                self.scope['visit_info_uuid'] = visit_info_uuid
                await self.save_visit_info(
                    id_visit_info = visit_info_uuid,
                    visitor = visitor_uuid,
                    ip_address = data["ip_address"],
                    location_approx = data["location_approx"],
                    visit_start_datetime = self.visit_start_datetime,
                )
                # mis à jour de la liste des visitInfo
                VisitorTrackerConsumer.list_visit_info.append(visit_info_uuid)

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
                    'is_read': False,
                }
            # Diffuser le message à l'app wooseeandy
            await self.channel_layer.group_send(
                f"user_{WOOSEEANDY_TOKEN}",
                message_data
            )
            # mis en cache du message : visitor_data
            mes = cache.get(f"visit_info_data_{visit_info_uuid}", []) # get the cache, pour enregister une cache en liste
            mes.append(message_data)
            cache.set(f"visit_info_data_{visit_info_uuid}", mes, timeout=3600) # 1h
        
        # **************** DATA TYPE : CV-DOWNLOAD ****************
        elif data.get("type") == "cv-download" :
            id_cv_download = uuid.uuid4()
            while await self.check_cv_donwload_exists(id_cv_download):
                id_cv_download = uuid.uuid4()
                print('--inside while loop--')
            download_datetime = timezone.now() if timezone.now() else None
            await self.save_cv_download(id_cv_download = id_cv_download ,visitor_uuid = data["uuid"], download_datetime = download_datetime)
            message_data = {
                'type': 'cv_download_sender',
                'id_cv_download': str(id_cv_download),
                'uuid': str(data["uuid"]),
                'download_datetime': download_datetime.isoformat(),
                'is_read': False,
            }
            # Diffuser à wooseeandy
            await self.channel_layer.group_send(
                f"user_{WOOSEEANDY_TOKEN}",
                message_data
            )
            # mis à jour de la liste des cv_download
            VisitorTrackerConsumer.list_cv_download.append(id_cv_download)
            # mis en cache du message : cv_download
            mes = cache.get(f"cv_download_{data["uuid"]}", [])
            mes.append(message_data)
            cache.set(f"cv_download_{data["uuid"]}", mes, timeout=3600) # 1h

        # ***************** DATA TYPE : PORTFOLIO-DETAILS-VIEW ******************
        elif data.get("type") == "portfolio_details_view" :
            id_portfolio_detail_view = uuid.uuid4()
            while await self.check_portfolio_detail_view_exists(id_portfolio_detail_view):
                id_portfolio_detail_view = uuid.uuid4()
                print('--inside while loop--')
            view_datetime = timezone.now() if timezone.now() else None
            await self.save_portfolio_detail_view(
                id_portfolio_detail_view = id_portfolio_detail_view,
                visitor_uuid = data["uuid"],
                project_name = data["project_name"],
                project_type = data["project_type"],
                view_datetime = view_datetime
                )
            message_data = {
                'type': 'portfolio_details_view_sender',
                'id_portfolio_detail_view': str(id_portfolio_detail_view),
                'visitor_uuid': str(data["uuid"]),
                'project_name': data["project_name"],
                'project_type': data["project_type"],
                'view_datetime': view_datetime.isoformat(),
                'is_read': False,
            }
            await self.channel_layer.group_send(
                f"user_{WOOSEEANDY_TOKEN}",
                message_data
            )
            # mis à jour de la liste des portfolio_detail_view
            VisitorTrackerConsumer.list_portfolio_detail_view.append(id_portfolio_detail_view)
            # mis en cache du message : portfolio_detail_view
            mes = cache.get(f"portfolio_detail_view_{data["uuid"]}", [])
            mes.append(message_data)
            cache.set(f"portfolio_detail_view_{data["uuid"]}", mes, timeout=3600) # 1h



    # _______________RECEIVE FROM WOOSEEANDY________________
    async def receive_from_wooseeandy(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json['data']
        # **** update server cache ****
        if data.get("type") == "update_server_cache":
            if data.get("cache_type") == "data_api":
                visit_info_uuid = data.get("uuid")
                cache_data = cache.get(f"visit_info_data_{visit_info_uuid}", [])
                if cache_data :
                    for c in cache_data :
                        c["is_read"] = True
                        cache.set(f"visit_info_data_{visit_info_uuid}", cache_data, timeout=3600)
            
            elif data.get("cache_type") == "cv_download_alert":
                cv_download_uuid = data.get("uuid")
                cache_data = cache.get(f"cv_download_{cv_download_uuid}", [])
                if cache_data :
                    for c in cache_data :
                        c["is_read"] = True
                        cache.set(f"cv_download_{cv_download_uuid}", cache_data, timeout=3600)

            elif data.get("cache_type") == "portfolio_details_view_alert":
                portfolio_detail_view_uuid = data.get("uuid")
                cache_data = cache.get(f"portfolio_detail_view_{portfolio_detail_view_uuid}", [])
                if cache_data :
                    for c in cache_data :
                        c["is_read"] = True
                        cache.set(f"portfolio_detail_view_{portfolio_detail_view_uuid}", cache_data, timeout=3600)
    
    
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
        is_read = event['is_read']

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
            'is_read': is_read,
        }))
    async def disconnect_alert_sender(self, event):
        new_visitor = event['is_new_visitor'] # bool, permet de savoir si le visiteur déconnecté est un nouveau ou pas
        end_datetime = event['end_datetime']
        id_visit_info = event['visit_info_uuid']
        visit_duration = event['visit_duration']
        await self.send(text_data=json.dumps({
            'alert_type': 'disconnected_alert',  # ceci permet de distinguer les types d'alerte en wooseeandy app
            'is_new_visitor': new_visitor,
            'visit_info_uuid': id_visit_info,
            'visit_end_datetime': end_datetime,
            'visit_duration': visit_duration,
        }))
    
    async def cv_download_sender(self, event):
        id_cv_download = event['id_cv_download']
        visitor_uuid = event['uuid']
        download_datetime = event['download_datetime']
        is_read = event['is_read']
        await self.send(text_data=json.dumps({
            'alert_type': 'cv_download_alert',
            'id_cv_download': id_cv_download,
            'visitor_uuid': visitor_uuid,
            'download_datetime': download_datetime,
            'is_read': is_read,
        }))
    
    async def portfolio_details_view_sender(self, event):
        id_portfolio_detail_view = event['id_portfolio_detail_view']
        visitor_uuid = event['visitor_uuid']
        project_name = event['project_name']
        project_type = event['project_type']
        view_datetime = event['view_datetime']
        is_read = event['is_read']
        await self.send(text_data=json.dumps({
            'alert_type': 'portfolio_details_view_alert',
            'id_portfolio_detail_view': id_portfolio_detail_view,
            'visitor_uuid': visitor_uuid,
            'project_name': project_name,
            'project_type': project_type,
            'view_datetime': view_datetime,
            'is_read': is_read,
        }))
    
    # ======================== DATABASE ==========================

    @database_sync_to_async
    def update_visitor_state(self, visitor_uuid, is_new_visitor):
        visitor = Visitor.objects.get(id_visitor=visitor_uuid)
        if visitor:
            visitor.is_new_visitor = is_new_visitor
            visitor.save()

    @database_sync_to_async
    def check_visitor_exists(self, visitor_uuid):
        return Visitor.objects.filter(id_visitor = visitor_uuid).exists()
    
    @database_sync_to_async
    def check_visit_info_exists(self, visit_info_uuid):
        return VisitInfo.objects.filter(id_visit_info = visit_info_uuid).exists()

    @database_sync_to_async
    def check_cv_donwload_exists(self, id_cv_download):
        return CVDownload.objects.filter(id_cv_download = id_cv_download).exists()
    
    @database_sync_to_async
    def check_portfolio_detail_view_exists(self, id_portfolio_detail_view):
        return PortfolioDetailView.objects.filter(id_portfolio_detail_view = id_portfolio_detail_view).exists()
    
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
    
    @database_sync_to_async
    def save_cv_download(self, id_cv_download, visitor_uuid, download_datetime):
        visitor_instance = Visitor.objects.get(id_visitor=visitor_uuid)
        return CVDownload.objects.create(
            id_cv_download = id_cv_download,
            visitor = visitor_instance,
            download_datetime = download_datetime            
            )
    
    @database_sync_to_async
    def save_portfolio_detail_view(self, id_portfolio_detail_view, visitor_uuid, project_name, project_type, view_datetime):
        visitor_instance = Visitor.objects.get(id_visitor=visitor_uuid)
        return PortfolioDetailView.objects.create(
            id_portfolio_detail_view = id_portfolio_detail_view,
            visitor = visitor_instance,
            project_name = project_name,
            project_type = project_type,
            view_datetime = view_datetime)