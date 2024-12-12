from rest_framework import serializers

from .models import UserModel
from admins.models import GasStationModel
from .constants import ACTION, CREATE


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

class PointSerializer(serializers.Serializer):
    point = serializers.ListField(child=serializers.DecimalField(max_digits=9, decimal_places=6), min_length=2, max_length=2)

