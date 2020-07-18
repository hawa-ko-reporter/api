import requests
from datetime import timedelta, time, datetime

from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.timezone import make_aware
from subscriptions.models import UserSubscription

from subscriptions.helpers.facebook_api import FacebookMessage

from subscriptions.helpers.air_quality_fetcher import AirQualityFetcher

from subscriptions.helpers.air_quality_fetcher import prepare_aqi_message
from subscriptions.helpers.dialog_flow_response import DialogFlowMessage

today = timezone.now()
tomorrow = today + timedelta(1)
today_start = make_aware(datetime.combine(today, time()))
today_end = make_aware(datetime.combine(tomorrow, time()))
import os


class Command(BaseCommand):
    help = "Send Today's AQI to subscribers"
    text_message = ""

    facebook_access_token = os.environ.get('FB_ACCESS_TOKEN', '').strip()
    aqi_token = os.environ.get('AQI_TOKEN', '').strip()

    def handle(self, *args, **options):
        user_subs = UserSubscription.objects.filter(is_archived=False)
        aqi_fetcher = AirQualityFetcher(aqi_token=self.aqi_token)
        fb_msg = FacebookMessage(access_token=self.facebook_access_token)

        if user_subs:
            messages = ["🙄", "Your daily hawa ko report has arrived", ""]

            for user_sub in user_subs:
                platform_id = user_sub.subscription_user.platform_id
                station_id = user_sub.subscription.id

                station = aqi_fetcher.get_by_station_id(station_id=station_id)

                messages = messages + prepare_aqi_message(station)
                message_to_send = "\n".join(messages)

                fb_msg.send_message(platform_id, message_to_send)

                self.stdout.write(platform_id)
            self.stdout.write("AQI report was sent was sent to {} subscribers".format(len(user_subs)))
        else:
            self.stdout.write("No subscribers to sent")
