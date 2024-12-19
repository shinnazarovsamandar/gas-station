from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError

from django.core.cache import cache
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .serializers import (SignUpModelSerializer, VerifyModelSerializer,
                          UserDetailsModelSerializer, TokenModelSerializer,
                          DisconnectSerializer,)
from .tasks import send_sms_task
from .utils import generate_code, get_user

from .constants import USER
from .models import UserModel
from config.utils import create_response_body
from .utils import delete_gas_station_user
from admins.models import GasStationModel
from config.settings import env
# Create your views here.

class AuthCreateAPIView(generics.CreateAPIView):
    serializer_class = SignUpModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        # code = generate_code()
        #
        # timeout, key, value = 60, f"user_{phone_number}_{code}", {}
        timeout = 60
        timestamp = int(timezone.now().timestamp()) + timeout
        #
        # #save code to cache
        # cache.set(key, value, timeout)
        #
        # #send sms
        # send_sms_task.delay(phone_number, code)
        #
        data = {
            "timestamp": timestamp,
        }

        headers = self.get_success_headers(serializer.data)
        return Response(create_response_body("Code sent successfully.", data), headers=headers)

class VerifyCreateAPIView(generics.CreateAPIView):
    serializer_class = VerifyModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        #verify code
        phone_number = serializer.validated_data['phone_number']
        # code = serializer.validated_data['code']
        #
        # key = f"user_{phone_number}_{code}"
        #
        # get_key = cache.get(key)
        #
        # if get_key is None:
        #     return Response(create_response_body("Invalid code."), status=status.HTTP_400_BAD_REQUEST)
        #
        # cache.delete(key)

        try:
            user = get_user(phone_number, USER)
        except UserModel.DoesNotExist:
            user = UserModel.objects.create(phone_number=phone_number)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        data = {
            "access": str(access),
            "refresh": str(refresh),
            "is_signed_up": user.is_signed_up,
            "id": user.id
        }
        headers = self.get_success_headers(serializer.data)
        return Response(create_response_body("Code verified successfully.", data), headers=headers)

class UserDetailsUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserDetailsModelSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['put']




    def perform_update(self, serializer):
        user = serializer.instance

        if user.is_signed_up:
            raise ValidationError("User has already signed up and cannot update the details.")
        serializer.save(is_signed_up=True)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(create_response_body("User details created successfully."))
    def get_object(self):
        return self.request.user

class TokenCreateAPIView(generics.CreateAPIView):
    serializer_class = TokenModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data['refresh']
        try:
            refresh = RefreshToken(refresh)
            access = refresh.access_token
            data = {
                "access": str(access)
            }
            headers = self.get_success_headers(serializer.data)

            return Response(create_response_body("Access token created successfully.", data), headers=headers)
        except TokenError:
            return Response(create_response_body("Invalid refresh token."), status=status.HTTP_400_BAD_REQUEST)

class SignOutAPIView(generics.CreateAPIView):
    permission_classes = ()

class DeleteDestroyAPIView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        user.delete()
        return Response(create_response_body("User deleted successfully."))


from rest_framework.views import APIView

class DisconnectAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        message, data = delete_gas_station_user(user)
        if message is not None:
            channel_layer = get_channel_layer()
            group_name = "chat_gas_stations"

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "chat_message",
                    "message": data
                }
            )


        return Response(create_response_body("Disconnect user successfully."))

class VersionAPIView(APIView):

    def get(self, request, *args, **kwargs):

        data = {
            "version": env("VERSION")
        }
        return Response(create_response_body("Version retreived successfully.", data))

