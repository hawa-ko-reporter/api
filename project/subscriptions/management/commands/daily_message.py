import requests
from datetime import timedelta, time, datetime

from django.core.management import BaseCommand
from django.db.models import Min
from django.utils import timezone
from django.utils.timezone import make_aware
from subscriptions.models import UserSubscription

from subscriptions.helpers.facebook_api import FacebookMessage

from subscriptions.helpers.air_quality_fetcher import AirQualityFetcher

from subscriptions.helpers.air_quality_fetcher import prepare_aqi_message
from subscriptions.helpers.dialog_flow_response import DialogFlowMessage

from subscriptions.models import Program

from subscriptions.helpers.numbers_to_words import n2w

today = timezone.now()
tomorrow = today + timedelta(1)
today_start = make_aware(datetime.combine(today, time()))
today_end = make_aware(datetime.combine(tomorrow, time()))
import os

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    text_message = ""

    facebook_access_token = os.environ.get('FB_ACCESS_TOKEN', '').strip()
    aqi_token = os.environ.get('AQI_TOKEN', '').strip()
    sent_platform_ids = {}
    fb_msg = None

    today = timezone.now()

    def check_for_every_subs(self, user_subs):

        total_content_count = Program.objects.all().count()
        for user_sub in user_subs:
            platform_id = user_sub.subscription_user.platform_id
            if self.sent_platform_ids.__contains__(platform_id):
                continue

            self.sent_platform_ids[platform_id] = True

            delta = (datetime.now().date() + timedelta(1)) - user_sub.created.date()
            delta_day = delta.days
            day_content = Program.objects.filter(reveal_day=delta_day).first()

            messages_to_send = ["Day #{} :) ".format(delta_day),
                                "",
                                day_content.name,
                                "",
                                day_content.description]

            message_to_send = "\n".join(messages_to_send)
            print(message_to_send)
            res = self.fb_msg.send_message(platform_id, message_to_send)

            message = {
                platform_id
            }
            self.stdout.write(str(res))

    def handle(self, *args, **options):
        # TODO: replace with .distinct()
        user_subs = UserSubscription.objects.filter(is_archived=False, )
        self.fb_msg = FacebookMessage(access_token=self.facebook_access_token)

        if user_subs:
            self.check_for_every_subs(user_subs=user_subs)
            self.stdout.write("Daily messages has been sent {} subscribers".format(len(self.sent_platform_ids)))
        else:
            self.stdout.write("No subscribers to sent")
