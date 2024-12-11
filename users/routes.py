from django.urls import path
from channels.routing import URLRouter
from .consumers import GasStationsAsyncWebsocketConsumer
ws_urlpatterns = [
    path("test/", GasStationsAsyncWebsocketConsumer.as_asgi())
]