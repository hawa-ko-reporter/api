import requests
import os
import json
from datetime import timedelta, time, datetime
from django.db.models import Q
from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.timezone import make_aware
from subscriptions.models import UserSubscription

from subscriptions.helpers.facebook_api import FacebookMessageSender

from subscriptions.helpers.air_quality_fetcher import AirQualityFetcher

from subscriptions.helpers.air_quality_fetcher import prepare_aqi_message
from subscriptions.helpers.dialog_flow_response import DialogFlowMessage
from django.utils.timezone import localdate, localtime

from subscriptions.helpers.dialog_flow_response import prepare_aqi_message_v2

from subscriptions.helpers.dialog_flow_response import fb_card_message

from subscriptions.helpers.air_quality_fetcher import get_aqi_code
from subscriptions.models import Recommendation, SubscriptionDelivery

from subscriptions.helpers.geo import distance


class Command(BaseCommand):
    help = "Send Today's AQI to subscribers"
    text_message = ""

    facebook_access_token = os.environ.get('FB_ACCESS_TOKEN', '').strip()
    aqi_token = os.environ.get('AQI_TOKEN', '').strip()

    def handle(self, *args, **options):
        user_subs = UserSubscription.objects.filter(is_archived=False, start_time__lte=localtime(),
                                                    end_time__gte=localtime())
        aqi_fetcher = AirQualityFetcher(aqi_token=self.aqi_token)
        fb_msg = FacebookMessageSender(access_token=self.facebook_access_token)

        if user_subs:
            for user_sub in user_subs:
                platform_id = user_sub.subscription_user.platform_id
                station_name = user_sub.subscription.name
                delivery = SubscriptionDelivery.objects.filter(
                    Q(delivery_status=200),
                    delivery_user=user_subs[0].subscription_user,
                    created__startswith=str(localdate()),

                ).order_by('-created').count()

                if delivery >= 1:
                    continue

                aqi = aqi_fetcher.get_by_station_id(station_name=station_name)
                if not aqi:
                    self.stdout.write("Selected station not offline -- pull data from another station")
                    aqi = aqi_fetcher.get_by_distance(lat=user_sub.subscription.latitude,
                                                      lon=user_sub.subscription.longitude)

                aqi_code, health = get_aqi_code(aqi=aqi['aqi'])
                recommendation = Recommendation.objects.filter(recommendation_category=aqi_code).order_by('?').first()

                aqi['message'] = recommendation.recommendation_text
                aqi['health'] = health
                aqi['street_display_name'] = user_sub.subscription_location_name
                aqi['distance'] = distance(user_sub.subscription_location_latitude,
                                           user_sub.subscription_location_longitude,
                                           aqi.get('lat'),
                                           aqi.get('lon')
                                           )

                messages = prepare_aqi_message_v2(aqi)

                response, status_code = fb_msg.send_card_message(platform_id, messages)

                SubscriptionDelivery.objects.create(
                    delivery_user=user_sub.subscription_user,
                    delivery_status=status_code,
                    delivery_location_name=aqi['station']['name'],
                    delivery_aqi=aqi['aqi'],
                    delivery_status_message=response
                )

                self.stdout.write("Report sent to {} with status code {} ".format(user_sub.subscription_user,status_code))



