from celery import shared_task
from .utils import send_sms

@shared_task
def send_sms_task(phone_number, code):
    send_sms(phone_number, code)
    return "success"