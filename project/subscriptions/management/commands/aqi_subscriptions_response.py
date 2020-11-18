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

from subscriptions.helpers.dialog_flow_response import get_aqi_message, fb_template_card

from subscriptions.helpers.dialog_flow_response import fb_text


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

                # aqi = aqi_fetcher.get_by_station_id(station_name=station_name)
                self.stdout.write("Selected station offline -- pull data from another station")
                stations = aqi_fetcher.get_by_distance(lat=user_sub.subscription_location_latitude,
                                                      lon=user_sub.subscription_location_longitude,results=3)

                aqi_code, health = get_aqi_code(aqi=stations[0]['aqi'])
                recommendation = Recommendation.objects.filter(recommendation_category=aqi_code).order_by('?').first()


                elements = []
                for station in stations:

                    image_url, message = get_aqi_message(station['aqi'])
                    full_url = 'https://hawa.naxa.com.np/aqi/?id={}'.format(station['uid'])


                    station_name = station.get('station').get('name')
                    title = "{} ({:.1f} KM away)".format(station_name, station['distance'])
                    aqi_code, health = get_aqi_code(aqi=station['aqi'])
                    message = "This is considered {} ".format(health)

                    elements.append(
                        fb_template_card(title=title,
                                         image_url=image_url,
                                         maps_url=full_url,
                                         message=message
                                         ))
                    if recommendation is None:
                        recommendation = Recommendation.objects.filter(recommendation_category=aqi_code).order_by(
                            '?').first()
                        if recommendation is not None:
                            recommendation = "I would say {}".format(recommendation.recommendation_text)

                fb_custom_payload = {

                    'payload': {
                        'facebook': {
                            'attachment': {'type': 'template', 'payload': {'template_type': 'generic',
                                                                           'elements': elements}}
                        }
                    },
                    'platform': "FACEBOOK"
                }

                fb_msg.send_text_message(platform_id, "Your daily report for *{}* has arrived".format(
                    user_sub.subscription_location_name))

                response, status_code = fb_msg.send_card_message(platform_id, fb_custom_payload['payload']['facebook']['attachment'])
                SubscriptionDelivery.objects.create(
                    delivery_user=user_sub.subscription_user,
                    delivery_status=status_code,
                    delivery_location_name=stations[0]['station']['name'],
                    delivery_aqi=stations[0]['aqi'],
                    delivery_status_message=response
                )

                self.stdout.write("Report sent to {} with status code {} ".format(user_sub.subscription_user,status_code,response))



