from rest_framework import serializers
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import Point
from rest_framework_gis import serializers
from .models import GasStationModel


class GasStationGeoFeatureModelSerializer(serializers.GeoFeatureModelSerializer):
    class Meta:
        model = GasStationModel
        geo_field = 'point'
        fields = ['name', 'point']

class GasStationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GasStationModel
        fields = ['id', 'name', 'point']
