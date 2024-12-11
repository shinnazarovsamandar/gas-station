from rest_framework import serializers
from .models import UserModel
from admins.models import GasStationModel

class SignUpModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['phone_number']

class VerifyModelSerializer(serializers.ModelSerializer):
    code = serializers.CharField()
    class Meta:
        model = UserModel
        fields = ['phone_number', 'code']

class UserDetailsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['name', 'number']

class TokenModelSerializer(serializers.Serializer):
    refresh = serializers.CharField()



