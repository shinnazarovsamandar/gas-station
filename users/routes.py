from django.urls import path
from channels.routing import URLRouter
from .consumers import GasStationsAsyncWebsocketConsumer, GasStationAsyncWebsocketConsumer
ws_urlpatterns = [
    path("gas-stations/", GasStationsAsyncWebsocketConsumer.as_asgi()),
    path("gas-station/<uuid:id>/", GasStationAsyncWebsocketConsumer.as_asgi())
]