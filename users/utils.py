import string
import secrets
from eskiz.client.sync import ClientSync
from eskiz.exception.token import TokenExpired

from config.settings import env
from .models import UserModel


def send_sms(phone_number, code):
    eskiz_client = ClientSync(
        email=env("ESKIZ_EMAIL"),
        password=env("ESKIZ_PASSWORD"),
    )
    def send_sms_eskiz():
        text = f"{env('ESKIZ_TEXT')} {code}"

        eskiz_client.send_sms(
            phone_number=int("998" + phone_number),
            message=text
        )
    try:
        send_sms_eskiz()
    except TokenExpired:
        eskiz_client.login()
        send_sms_eskiz()

def generate_code(length=4):
    digits = string.digits
    code = ''.join(secrets.choice(digits) for _ in range(length))
    return code

def get_user(phone_number, type):
    user = UserModel.objects.get(phone_number=phone_number, type=type)
    return user

def delete_gas_station_user(user):
    gas_station_user = user.gas_station_users.first()
    if gas_station_user:
        gas_station = gas_station_user.gas_station
        gas_station.total-=1
        gas_station.save()
        gas_station_user.delete()
        if gas_station.is_open and gas_station.total <= int(env('TOTAL')):
            gas_station.is_open = False
            gas_station.save()
        message = "Gas station user deleted successfully."
        data = {
            "action": DELETE,
            "user": {
                "id": str(self.user.id)
            },
            "gas_station": {
                "id": str(gas_station.id),
                "total": gas_station.total,
                'is_open': gas_station.is_open
            }
        }
        return message, data
    return None, None
