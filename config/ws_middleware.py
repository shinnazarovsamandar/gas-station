from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from users.models import UserModel

@database_sync_to_async
def get_user(user_id):
    try:
        return UserModel.objects.get(id=user_id)
    except UserModel.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        token = headers.get(b'authorization').decode()

        if token:
            try:
                access_token = AccessToken(token)
                scope["user"] = await get_user(access_token["user_id"])
            except TokenError:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()
        # try:
        return await self.app(scope, receive, send)
        # except Exception as e:

        #     await send({
        #         "type": "websocket.close",
        #     })