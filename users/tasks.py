from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from datetime import timedelta

from .utils import send_sms, delete_gas_station_user
from users.models import UserModel
@shared_task
def send_sms_task(phone_number, code):
    send_sms(phone_number, code)
    return "success"

def my_cron_job():
    users = UserModel.objects.all()
    for user in users:
        if user.updated_at < timezone.now() - timedelta(minutes=1):
            message, data = delete_gas_station_user(user)
            if message is not None:
                channel_layer = get_channel_layer()
                group_name = "chat_gas_stations"

                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "chat_message",
                        "message": data
                    }
                )