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