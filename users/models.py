from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

#custom import
from config.models import BaseModel
from .managers import UserManager
from .constants import  (
    TYPE_CHOICES, USER
)
from admins.models import GasStationModel

# Create your models here.

#user model
class UserModel(AbstractUser, BaseModel):
    phone_number = models.CharField(max_length=9, validators=[RegexValidator(regex=r'^\d{9}$', message='Field must contain exactly 9 digits')])
    name = models.CharField(max_length=50, null=True)
    number = models.CharField(max_length=30, null=True)
    point = models.PointField(null=True)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=USER)
    username = models.CharField(max_length=50, unique=True)
    is_signed_up = models.BooleanField(default=False)

    #remove fields
    first_name = None
    last_name = None
    last_login = None
    is_staff = None
    is_superuser = None
    email = None
    date_joined = None
    password = None

    objects = UserManager()
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.phone_number + self.type
        super().save(*args, **kwargs)

class GasStationUserModel(BaseModel):
    gas_station = models.ForeignKey(GasStationModel, on_delete=models.CASCADE, related_name="gas_station_users")
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="gas_station_users")

