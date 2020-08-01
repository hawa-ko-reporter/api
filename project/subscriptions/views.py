# Create your views here.
import json
import os
import random
import traceback

import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import MessageForm
from .helpers.consts import messages
from .helpers.air_quality_fetcher import getNearestAQI, get_aqi_code
from .helpers.dialog_flow_response import get_aqi_response_message, single_line_message, get_list_subs_response_message
from .helpers.facebook_api import get_name, handle_fb_name_response
from .models import User, UserSubscription, Subscription, AQIRequestLog, Recommendation
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

    @staticmethod
    def prepare_message(data):
        message = "The nearest station is {}".format(data['station']['name'])
        message += " \n "
        message += "It is {:.1f} km away".format(data['distance'])
        message += " "
        message += "The AQI is {} at {}".format(
            data['message']['level'], data['aqi'])
        message += " \n "
        message += " \n "
        message += "I would say {} ".format(data['message']['health'])
        message += "Do you want more tips?"
        return message

    def load_user_data_from_fb(self, data):
        platform_id = data['originalDetectIntentRequest']['payload']['data']['sender']['id']
        platform = data['originalDetectIntentRequest']["source"]
        content = get_name(platform_id, self.facebook_access_token)
        name = handle_fb_name_response(content, '')

        return platform, platform_id, name

    def save_aqi_request_to_log(self, data, subscription, recommendation):
        platform, platform_id, name = self.load_user_data_from_fb(data)
        user, created = User.objects.get_or_create(
            platform=platform,
            platform_id=platform_id,
            full_name=name
        )

        AQIRequestLog.objects.create(
            user=user,
            subscription=subscription,
            recommendation=recommendation
        )

    def handleAQIRequest(self, data):
        address = data['queryResult']['parameters']['address']
        geo_location = self.reverseGeocode(address)
        aqi = getNearestAQI(
            float(geo_location[0]), float(geo_location[1]))

        if aqi:
            aqi['query'] = address
            aqi_code, health = get_aqi_code(aqi=aqi['aqi'])
            recommendation = Recommendation.objects.filter(recommendation_category=aqi_code).order_by('?').first()
            subscription = Subscription.objects.get(name=aqi['station']['name'])

            aqi['message'] = recommendation.recommendation_text
            aqi['health'] = health

            self.save_aqi_request_to_log(data, subscription, recommendation)
            return get_aqi_response_message(aqi, data)
        else:
            return single_line_message(message="No nearby stations found! 😶")

    def handleMaskQuery(self, data):
        address = data['queryResult']['parameters']['address']
        geo_location = self.reverseGeocode(address)
        aqi = getNearestAQI(
            float(geo_location[0]), float(geo_location[1]))
        if aqi:
            aqi['query'] = address
            aqi['message'] = self.getAQIMessage(float(aqi['aqi']))
            return single_line_message(message=aqi['message']['health'])
        else:
            return single_line_message(message="No nearby stations found! 😶")

    def handleUnsubscribe(self, data):
        platform, platform_id, name = self.load_user_data_from_fb(data)
        user = User.objects.get(platform=platform, platform_id=platform_id)
        UserSubscription.objects.select_related().filter(subscription_user=user,
                                                         is_archived=False).update(is_archived=True)

        return single_line_message(message="You have been unsubscribed")

    def handleListSubscriptions(self, data):
        platform, platform_id, name = self.load_user_data_from_fb(data)

        user = User.objects.get(platform=platform, platform_id=platform_id)
        subscriptions = UserSubscription.objects.select_related().filter(subscription_user=user, is_archived=False)

        if subscriptions:
            return get_list_subs_response_message(subscriptions=subscriptions)

        return single_line_message(message="You do not have any subscriptions")

    def handleSubscribeRequest(self, data):
        platform, platform_id, name = self.load_user_data_from_fb(data)
        address = data['queryResult']['parameters']["address"]
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
        return single_line_message("You will now receive daily updates for {} 🎉🎉🎉".format(address))

    def handleAQIMessageRequest(self, data):
        aqi = data['queryResult']["outputContexts"][0]['parameters']['aqi']

        message = self.getAQIMessage(aqi)
        message = message['health']
        return single_line_message(message)

    def post(self, request):
        try:
            data = request.data
            intent = data['queryResult']['intent']['displayName']
            print(intent)
            if intent == "request.aqi":
                message = self.handleAQIRequest(data)
            elif intent == "request.aqi-yes":
                message = self.handleAQIMessageRequest(data)
            elif intent == "daily.subscribe":
                message = self.handleSubscribeRequest(data)
            elif intent == "daily.unsubscribe":
                message = self.handleListSubscriptions(data)
            elif intent == "daily.unsubscribe - yes":
                message = self.handleUnsubscribe(data)
            elif intent == "query.do-i-need-mask":
                message = self.handleMaskQuery(data)
            else:
                raise Exception("Not supported")
            return Response(data=message)
        except:
            print(traceback.format_exc())
            return Response(data=single_line_message("No data avaliable"))


def message_new(request):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
    else:
        form = MessageForm()
    return render(request, 'subscriptions/message_edit.html', {'form': form})
