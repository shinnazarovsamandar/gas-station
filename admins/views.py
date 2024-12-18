from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from config.utils import create_response_body


from .models import GasStationModel
from .serializers import GasStationGeoFeatureModelSerializer
# Create your views here.
class GasStationCreateAPIView(generics.CreateAPIView):
    queryset = GasStationModel.objects.all()
    serializer_class = GasStationGeoFeatureModelSerializer
    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(create_response_body("Gas-Station created successfully."), headers=headers)

class GasStationListAPIView(generics.ListAPIView):
    queryset = GasStationModel.objects.all()
    serializer_class = GasStationGeoFeatureModelSerializer
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().order_by("-created_at")
        serializer = self.get_serializer(queryset, many=True)

        data = {
            "gas-stations": serializer.data
        }
        return Response(create_response_body("Gas stations retreived successfully.", data))