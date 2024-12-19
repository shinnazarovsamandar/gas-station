import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from django.contrib.gis.geos import Point
from django.utils import timezone
from geopy.distance import distance as geopy_distance


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

    async def disconnect(self, close_code):
        if close_code != 1006:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            message, data = await database_sync_to_async(self.delete_gas_station_user)()
            if message is not None:
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
                message, data, delete_message, delete_data = await self.create_point(serializer.data)
                if message is not None:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': create_response_body(message, data)
                        }
                    )
                else:
                    if delete_message is not None:
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'chat_message',
                                'message': create_response_body(delete_message, delete_data)
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
                    if message is not None:
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'chat_message',
                                'message': create_response_body(message, data)
                            }
                        )

                except Exception:
                    await self.close()
                    return
        elif action == LIST:
            data = await self.get_gas_stations()
            data = {
                "action": LIST,
                "gas_stations": data
            }
            await self.send(text_data=json.dumps(
                create_response_body("Gas stations retrieved successfully.", data = data)
            ))
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
        # point = point.transform(3857)
        gas_stations = GasStationModel.objects.all()
        min_distance = float('inf')
        if gas_stations:
            closest_gas_station = None
            for gas_station in gas_stations:
                distance = geopy_distance(point, gas_station.point).meters
                print(self.user.name, self.user.phone_number, distance)
                if distance <= int(env('DISTANCE')) and distance <= min_distance:
                    min_distance = distance
                    closest_gas_station = gas_station
            if closest_gas_station is not None:
                gas_station_user_ = self.user.gas_station_users.all()
                if gas_station_user_:
                    serializer = UserPointModelSerializer(self.user)
                    gas_station = None
                    gas_station_user = gas_station_user_.filter(gas_station=closest_gas_station).first()
                    if gas_station_user is None:
                        gas_station = gas_station_user_.first().gas_station
                        gas_station.total-=1
                        gas_station.save()
                        gas_station_user_.delete()
                        GasStationUserModel.objects.create(gas_station=closest_gas_station, user=self.user)
                        closest_gas_station.total += 1
                        closest_gas_station.save()

                        if gas_station.is_open and gas_station.total == int(env('TOTAL')):
                            gas_station.is_open = False
                            gas_station.save()

                        if closest_gas_station.is_open == False and closest_gas_station.total > int(env('TOTAL')):
                            closest_gas_station.is_open = True
                            closest_gas_station.save()

                        gas_station = {
                            DELETE: {
                                'id': str(gas_station.id),
                                'total': gas_station.total,
                                'is_open': gas_station.is_open,
                            },
                            UPDATE: {
                                'id': str(closest_gas_station.id),
                                'total': closest_gas_station.total,
                                'is_open': closest_gas_station.is_open,
                            }
                        }

                    message = "Gas Station user updated successfully."
                    data = {
                        'action': UPDATE,
                        'user': serializer.data,
                        'gas_station': gas_station
                    }
                else:
                    GasStationUserModel.objects.create(gas_station=closest_gas_station, user=self.user)
                    closest_gas_station.total += 1
                    closest_gas_station.save()
                    if closest_gas_station.is_open == False and closest_gas_station.total > int(env('TOTAL')):
                        closest_gas_station.is_open = True
                        closest_gas_station.save()

                    serializer = UserDetailsModelSerializer(self.user)
                    serializer_gt = GasStationModelSerializer(closest_gas_station)
                    message = "Gas Station user created successfully."

                    data = {
                        "action": CREATE,
                        "user": serializer.data,
                        "gas_station": serializer_gt.data
                    }

                return message, data, None, None
            message, data = self.delete_gas_station_user()
            if message is not None:
                return None, None, message, data
        return None, None, None, None

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
            'action': COMMENT,
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

    def delete_gas_station_user(self):
        gas_station_user = self.user.gas_station_users.first()
        if gas_station_user is not None:
            gas_station = gas_station_user.gas_station
            gas_station.total-=1
            gas_station.save()
            gas_station_user.delete()
            if gas_station.is_open and gas_station.total == int(env('TOTAL')):
                gas_station.is_open = False
                gas_station.save()
            message = "Gas station user deleted successfully."
            data = {
                "action": DELETE,
                "user": {
                    "id": str(self.user.id)
                }, 
                "gas_station": {
                    "id": str(gas_station.id),
                    "total": gas_station.total,
                    'is_open': gas_station.is_open
                }
            }
            return message, data
        return None, None
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
