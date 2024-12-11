"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
django.setup()
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from channels.routing import ProtocolTypeRouter, URLRouter

#custom
from .ws_middleware import JWTAuthMiddleware as JWTAuthMiddlewareStack
from .routes import ws_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(
            ws_urlpatterns
        )
    ),
})