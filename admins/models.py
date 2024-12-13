from django.contrib.gis.db import models
from config.models import BaseModel
# Create your models here.
class GasStationModel(BaseModel):
    name = models.CharField(max_length=100)
    point = models.PointField(srid=4326)
    total = models.PositiveIntegerField(default=0)
    comment = models.CharField(max_length=255, null=True)
    comment_updated_at = models.DateTimeField(null=True)