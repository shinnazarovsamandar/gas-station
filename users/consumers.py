import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from django.contrib.gis.geos import Point
from django.utils import timezone


from config.utils import create_response_body
from .models import  GasStationModel, GasStationUserModel
from .constants import CREATE, UPDATE, LIST, DELETE, COMMENT
from .serializers import (PointSerializer, UserDetailsModelSerializer,
                          UserPointModelSerializer, GasStationModelSerializer,
                          GasStationUserModelSerializer, GasStationCommentModelSerializer)
from config.settings import env

class GasStationsAsyncWebsocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user.is_authenticated:
            await self.close()
            return

        # Get the room name from the query parameters
        self.room_name = f'gas_stations'  # Customize the room name
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        data = await self.get_gas_stations()
        data = {
            "action": LIST,
            "gas_stations": data
        }
        await self.send(text_data=json.dumps(
            create_response_body("Gas stations retrieved successfully.", data = data)
        ))

    async def disconnect(self, close_code):
        if close_code != 1006:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print("HI")
            gas_station_user = self.user.gas_station_users.first()
            if gas_station_user:
                gas_station = gas_station_user.gas_station
                gas_station.total-=1
                gas_station.save()
                gas_station_user.delete()

            message = "Gas station user deleted successfully."
            data = {
                "action": DELETE,
                "user": {
                    "id": self.user.id
                }, 
                "gas_station": {
                    "id": gas_station.id,
                    "total": gas_station.total
                }
            }
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': create_response_body(message, data)
                }
            )








    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        if action == CREATE:
            data = text_data_json['data']
            serializer = PointSerializer(data=data)
            if serializer.is_valid():
                message, data = await self.create_point(serializer.data)
                if message is not None:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': create_response_body(message, data)
                        }
                    )
            else:
                await self.close()
                return
        elif action == COMMENT:
            data = text_data_json['data']
            serializer = GasStationCommentModelSerializer(data=data)
            if serializer.is_valid():
                try:
                    message, data = await self.create_comment(serializer.data)
                except Exception:
                    await self.close()
                    return
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': create_response_body(message, data)
                    }
                )

        else:
            await self.close()
            return
        # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': message
        #     }
        # )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
    @database_sync_to_async
    def create_point(self, data):
        point = data['point']
        point = Point(list(map(float, point)))
        self.user.point = point
        self.user.save()

        gas_stations = GasStationModel.objects.all()
        for gas_station in gas_stations:
            distance = gas_station.point.distance(point)
            if distance <= int(env('DISTANCE')):
                gas_station_user = self.user.gas_station_users.filter(gas_station=gas_station).first()
                if gas_station_user is not None:
                    serializer = UserPointModelSerializer(self.user)
                    message = "Gas Station user updated successfully."
                    data = {
                        "action": UPDATE,
                        "user": serializer.data
                    }
                else:
                    GasStationUserModel.objects.create(gas_station=gas_station, user=self.user)
                    gas_station.total+=1
                    gas_station.save()
                    serializer = UserDetailsModelSerializer(self.user)
                    serializer_gt = GasStationModelSerializer(gas_station)
                    message = "Gas Station user created successfully."
                    data = {
                        "action": CREATE,
                        "user": serializer.data,
                        "gas_station": serializer_gt.data
                    }

                return message, data
        return None, None

    @database_sync_to_async
    def create_comment(self, data):
        id = data['id']
        comment = data['comment']
        updated_at = timezone.now()
        gas_station = GasStationModel.objects.get(id=id)
        gas_station.comment = comment
        gas_station.comment_updated_at = updated_at
        gas_station.save()
        message = "Gas station comment updated successfully."
        data = {
            "id": id,
            'comment': comment, 
            "updated_at": updated_at.isoformat()
        }
        return message, data
    
    @database_sync_to_async
    def get_gas_stations(self):
        gas_stations = GasStationModel.objects.all()
        serializer = GasStationUserModelSerializer(gas_stations, many=True)
        return serializer.data

# class GasStationAsyncWebsocketConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope.get("user")
#         if not self.user.is_authenticated:
#             await self.close()
#             return
#
#         try:
#             id = self.scope['url_route']['kwargs']['id']
#             await self.get_gas_station(id)
#         except Exception as e:
#             await self.close()
#             return
#
#         self.room_name = f'gas_station_{id}'  # Customize the room name
#         self.room_group_name = f'chat_{self.room_name}'
#
#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()
#
#         await self.send(text_data=json.dumps(
#             create_response_body("Gas stations. number of vehicles. retrieved successfully.", data = {})
#         ))
#
#     async def disconnect(self, close_code):
#         if close_code != 1006:
#             await self.channel_layer.group_discard(
#                 self.room_group_name,
#                 self.channel_name
#             )
#
#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )
#
#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event['message']
#
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))
#
#     @database_sync_to_async
#     def get_gas_station(self, id):
#         gas_station = GasStationModel.objects.get(id=id)
#         return gas_station
