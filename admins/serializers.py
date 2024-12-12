from rest_framework_gis.serializers import GeoFeatureModelListSerializer
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import Point
from rest_framework_gis import serializers
from .models import GasStationModel


from rest_framework import serializers
from django.contrib.gis.geos import Point

class GasStationGeoFeatureModelSerializer(GeoFeatureModelListSerializer):
    point = PointField()
    class Meta:
        model = GasStationModel
        geo_field = 'point'
        fields = ['name', 'point']

class GasStationModelSerializer(GeoFeatureModelListSerializer):
    class Meta:
        model = GasStationModel
        fields = ['id', 'name', 'point']
