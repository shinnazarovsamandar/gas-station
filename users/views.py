from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError

from django.core.cache import cache
from django.utils import timezone


from .serializers import (SignUpModelSerializer, VerifyModelSerializer,
                          UserDetailsModelSerializer, TokenModelSerializer)
from .tasks import send_sms_task
from .utils import generate_code, get_user

from .constants import USER
from .models import UserModel
from config.utils import create_response_body
from admins.models import GasStationModel
# Create your views here.

class AuthCreateAPIView(generics.CreateAPIView):
    serializer_class = SignUpModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        code = generate_code()

        timeout, key, value = 60, f"user_{phone_number}_{code}", {}
        timestamp = int(timezone.now().timestamp()) + timeout

        #save code to cache
        cache.set(key, value, timeout)

        #send sms
        send_sms_task.delay(phone_number, code)

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
        code = serializer.validated_data['code']

        key = f"user_{phone_number}_{code}"

        get_key = cache.get(key)

        if get_key is None:
            return Response(create_response_body("Invalid code."))

        cache.delete(key)

        try:
            user = get_user(phone_number, USER)
        except UserModel.DoesNotExist:
            user = UserModel.objects.create(phone_number=phone_number)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        data = {
            "access": str(access),
            "refresh": str(refresh),
            "is_signed_up": user.is_signed_up
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

