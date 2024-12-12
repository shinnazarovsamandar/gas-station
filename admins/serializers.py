from rest_framework_gis import serializers
from .models import GasStationModel

class GasStationGeoFeatureModelSerializer(serializers.GeoFeatureModelSerializer):
    class Meta:
        model = GasStationModel
        geo_field = 'point'
        fields = ['id', 'name', 'point']
        read_only_fields = ['id']
