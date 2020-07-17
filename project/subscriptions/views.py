# Create your views here.
import json
import os
import random
import traceback

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .helpers.consts import messages
from .helpers.air_quality_fetcher import AirQualityInfo
from .helpers.facebook_api import get_name, handle_fb_name_response
from .models import User, UserSubscription, Subscription
from .helpers.geo import distance


# Create your views here.
@api_view(["GET"])
@csrf_exempt
@permission_classes([AllowAny])
def welcome(request):
    content = {"message": "Welcome to Hawa-ko-reporter API!"}
    return JsonResponse(content)


class AirQualityIndexAPI(APIView):
    # https://api.waqi.info/feed/beijing/?token=9676b511e1f0fed7303343500998434a0d7b9245
    # https://aqicn.org/city/nepal/kathmandu/ratnapark/

    facebook_access_token = os.environ.get('FB_ACCESS_TOKEN', '').strip()
    geo_token = os.environ.get('GEO_TOKEN', '').strip()
    fullfillment_message = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages = messages

        self.air_quality_info = AirQualityInfo

    @staticmethod
    def dialogflow_message(message):
        return {'fulfillmentText': message}

    @staticmethod
    def dialogflow_message_list():
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Text response from webhook",
                            "Nishon",
                        ]
                    },

                }
            ]
        }

    def getAQIMessage(self, aqi):
        if aqi <= 50:
            return {"level": "Good", "health": random.choice(self.messages[0]), "caution": ""}
        elif aqi <= 100:
            return {"level": "Moderate", "health": random.choice(self.messages[1]), "caution": ""}
        elif aqi <= 150:
            return {"level": "Unhealthy for Sensitive Groups", "health": random.choice(self.messages[2]), "caution": ""}
        elif aqi <= 200:
            return {"level": "Unhealthy", "health": random.choice(self.messages[3]), "caution": ""},
        elif aqi <= 300:
            return {"level": "Very Unhealthy", "health": random.choice(self.messages[4]), "caution": ""}
        elif aqi > 300:
            return {"level": "Hazardous", "health": random.choice(self.messages[5]), "caution": ""}
        else:
            return {}

    def reverseGeocode(self, query):
        url = "https://us1.locationiq.com/v1/search.php"
        data = {
            'key': self.geo_token,
            'q': query,
            'format': 'json'
        }

        response = requests.get(url, params=data)
        obj = json.loads(response.text)

        return obj[0]['lat'], obj[0]['lon']

    def get(self, request):
        return Response(data="return msg or data")

    def prepareMessage(self, data):
        message = "The nearest station is {}".format(data['station']['name'])
        message += " \n "
        message += "It is {} km away".format(data['distance'])
        message += " "
        message += "The AQI is {} at {}".format(
            data['message']['level'], data['aqi'])
        message += " \n "
        message += " \n "
        message += "I would say {} ".format(data['message']['health'])
        message += "Do you want more tips?"
        return message

    def handleAQIRequest(self, data):
        address = data['queryResult']['parameters']['address']

        geo_location = self.reverseGeocode(address)
        print(geo_location)
        aqi = self.getNearestAQI(
            float(geo_location[0]), float(geo_location[1]))

        aqi['query'] = address
        aqi['message'] = self.getAQIMessage(float(aqi['aqi']))

        message = {
            'fulfillmentText': [
                self.prepareMessage(aqi),
            ],
            "outputContexts": [
                {
                    "name": "{}/contexts/data-upsell-yes".format(data['session']),
                    "lifespanCount": 5,
                    "parameters": {
                        "aqi": float(aqi['aqi']),
                    }
                }
            ]
        }
        return message

    def handleUnsubscribe(self, data):
        platform_id = data['originalDetectIntentRequest']['payload']['data']['sender']['id']
        platform = data['originalDetectIntentRequest']["source"]
        user = User.objects.get(platform=platform, platform_id=platform_id)
        UserSubscription.objects.select_related().filter(subscription_user=user,
                                                         is_archived=False).update(is_archived=True)
        self.fullfillment_message = "You have been unsubscribed"
        return self.dialogflow_message(message=self.fullfillment_message)

    def handleListSubscriptions(self, data):
        platform_id = data['originalDetectIntentRequest']['payload']['data']['sender']['id']
        platform = data['originalDetectIntentRequest']["source"]
        user = User.objects.get(platform=platform, platform_id=platform_id)
        subscriptions = UserSubscription.objects.select_related().filter(subscription_user=user, is_archived=False)

        if subscriptions:
            self.fullfillment_message = "You are subscribed to {} stations".format(len(subscriptions))
            for row in subscriptions:
                self.fullfillment_message += "\n"
                self.fullfillment_message += "\n"
                self.fullfillment_message += row.subscription.name

            self.fullfillment_message += "\n"
            self.fullfillment_message += "\n"
            self.fullfillment_message += "Do you want to un-subscribe?"
        else:
            self.fullfillment_message = "You do not have any subscriptions"
        return self.dialogflow_message(message=self.fullfillment_message)

    def handleSubscribeRequest(self, data):
        platform_id = data['originalDetectIntentRequest']['payload']['data']['sender']['id']
        platform = data['originalDetectIntentRequest']["source"]
        address = data['queryResult']['parameters']["Address"]

        content = get_name(platform_id, self.facebook_access_token)
        name = handle_fb_name_response(content, '')
        geo_location = self.reverseGeocode(address)

        user_lat = geo_location[0]
        user_lon = geo_location[1]

        user, created = User.objects.get_or_create(
            platform=platform,
            platform_id=platform_id,
            full_name=name
        )

        subscriptions = list(Subscription.objects.all().values())
        for subs in subscriptions:
            subs_lat = subs.get("latitude")
            subs_lon = subs.get("longitude")
            distance_in_km = distance(subs_lat, subs_lon, user_lat, user_lon)
            subs['distance'] = distance_in_km

        subscriptions.sort(key=lambda x: (x["distance"]))
        nearest_station_id = subscriptions[0].get('id')

        UserSubscription.objects.create(
            subscription_user=user,
            subscription=Subscription.objects.get(pk=nearest_station_id),
            subscription_location_name=address,
            subscription_location_latitude=user_lat,
            subscription_location_longitude=user_lon,
        )
        return self.dialogflow_message("You will now receive daily updates for {}".format(address))

    def handleAQIMessageRequest(self, data):
        aqi = data['queryResult']["outputContexts"][0]['parameters']['aqi']

        message = self.getAQIMessage(aqi)
        message = message['health']
        return self.dialogflow_message(message)

    def post(self, request):
        try:
            data = request.data
            intent = data['queryResult']['intent']['displayName']

            if intent == "request.aqi":
                message = self.handleAQIRequest(data)
            elif intent == "request.aqi-yes":
                message = self.handleAQIMessageRequest(data)
            elif intent == "subscribe":
                message = self.handleSubscribeRequest(data)
            elif intent == "unsubscribe":
                message = self.handleListSubscriptions(data)
            elif intent == "unsubscribe - yes":
                message = self.handleUnsubscribe(data)
            else:
                raise Exception("Not supported")
            return Response(data=message)
        except:
            print(traceback.format_exc())
            return Response(data=self.dialogflow_message("No data avaliable"))
