from django.urls import path
from channels.routing import URLRouter
from users import routes as users_routes

ws_urlpatterns = [
    path("ws/", URLRouter([
        path('user/', URLRouter(
            users_routes.ws_urlpatterns
        )),
    ])),
]