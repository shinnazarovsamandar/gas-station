from django.urls import path ,include

from .views import GasStationCreateAPIView, GasStationListAPIView

urlpatterns = [
    path('gas-station/', include([
        path('', GasStationCreateAPIView.as_view(), name='gas-station'),
        path('list/', GasStationListAPIView.as_view(), name='gas-station-list'),
    ]))
]