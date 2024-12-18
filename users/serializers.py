from rest_framework import serializers

from .models import UserModel, GasStationUserModel
from admins.models import GasStationModel
# from .constants import CREATE
from django.core.validators import RegexValidator



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
    name = serializers.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Zа-яА-ЯёЁ]+$",
                message="The name field must only contain letters without spaces."
            )
        ]
    )
    class Meta:
        model = UserModel
        fields = ['id', 'name', 'number', 'point']
        read_only_fields = ['id', 'point']

class TokenModelSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class PointSerializer(serializers.Serializer):
    point = serializers.ListField(child=serializers.DecimalField(max_digits=9, decimal_places=6), min_length=2, max_length=2)

class UserPointModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'point']

class GasStationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GasStationModel
        fields = ['id', 'total', 'is_open']

class _GasStationUserModelSerializer(serializers.ModelSerializer):
    user = UserPointModelSerializer()
    class Meta:
        model = GasStationUserModel
        fields = ['user']
class GasStationUserModelSerializer(serializers.ModelSerializer):
    gas_station_users = _GasStationUserModelSerializer(many=True)
    class Meta:
        model = GasStationModel
        fields = ['id', 'name', 'point', 'total', 'is_open', 'is_open_by_admin', 'comment', 'comment_updated_at', 'gas_station_users']

class GasStationCommentModelSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    comment = serializers.CharField(max_length=255)

class DisconnectSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    