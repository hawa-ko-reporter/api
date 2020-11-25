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
from .helpers.air_quality_fetcher import getNearestAQI, get_aqi_code, get_aqi, AirQualityFetcher
from .helpers.dialog_flow_parser import get_value_from_dialogflow_context, DIALOGFLOW_ADDRESS, DIALOGFLOW_TIME_PERIOD, \
    DIALOGFLOW_TIME_PERIOD_START, DIALOGFLOW_TIME_PERIOD_END
from .helpers.dialog_flow_response import get_aqi_response_message, single_line_message, get_list_subs_response_message, \
    multiple_stations_report, multiple_stations_slider_report_stations, welcome_message, confirm_geo_code_location,geocode_failure_reply,subscription_success_message
from .helpers.facebook_api import get_name, handle_fb_name_response
from .models import User, UserSubscription, Subscription, AQIRequestLog, Recommendation

from .helpers.geo import distance
from django.utils.dateparse import parse_date
from django.utils.dateparse import parse_datetime


# Create your views here.
@api_view(["GET"])
@csrf_exempt
@permission_classes([AllowAny])
def welcome(request):
    content = {"message": "Welcome to Hawa-ko-reporter API!"}
    return JsonResponse(content)


def get_address_from_dialogflow(data):
    address = data.get('queryResult').get('parameters').get('address')
    if not address:
        address = get_value_from_dialogflow_context(data, "address")
    return address


class AirQualityIndexAPI(APIView):
    # https://api.waqi.info/feed/beijing/?token=9676b511e1f0fed7303343500998434a0d7b9245
    # https://aqicn.org/city/nepal/kathmandu/ratnapark/

    facebook_access_token = os.environ.get('FB_ACCESS_TOKEN', '').strip()
    geo_token = os.environ.get('GEO_TOKEN', '').strip()
    fullfillment_message = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.was_request_success = False
        self.messages = messages

    def get_aqi_message(self, aqi):
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

    def reverse_geocode(self, query):
        error = ''
        url = "https://us1.locationiq.com/v1/search.php"
        data = {
            'key': self.geo_token,
            'q': query,
            'format': 'json',
            'countrycodes': 'np',
            'addressdetails': 1
        }

        response = requests.get(url, params=data)
        obj = json.loads(response.text)

        try:
            lat = obj[0]['lat']
            lon = obj[0]['lon']
            display_name = self.get_display_name(obj[0])
            return lat, lon, display_name, error
        except KeyError:
            error = 'Reverse geo-coding failed'
            return 0, 0, '', error

    def get_display_name(self,geocode_result):

        names = []
        address = geocode_result.get("address")
        display_name = geocode_result.get('display_name')

        # if "kathmandu" in display_name.lower():
        #     return display_name
        # if "lalitpur" in display_name.lower():
        #     return display_name

        # find address
        locality = address.get('road')

        if locality is None:
            locality = address.get('neighbourhood')

        if locality is None:
            locality = address.get('suburb')

        if locality is None:
            locality = address.get('locality')

        if locality is not None:
            names.append(locality)

            # find city
        city = address.get('town')

        if city is None:
            city = address.get('city')

        if city is None:
            city = address.get('county')

        if city is not None:
            names.append(city)

        print(names)
        if len(names) > 0:

            return ",".join(names)
        else:
            return display_name

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

    def save_aqi_request_to_log(self, data, location_name):
        try:
            platform, platform_id, name = self.load_user_data_from_fb(data)
            user, created = User.objects.get_or_create(
                platform=platform,
                platform_id=platform_id,
                full_name=name
            )

            AQIRequestLog.objects.create(
                user=user,
                location_name=location_name
            )
        except KeyError:
            print("Failed to save aqi request logs")

    def handleAQISummaryReport(self, data):
        address = data['queryResult']['parameters']['address']
        geo_location = self.reverse_geocode(address)
        stations = get_aqi(float(geo_location[0]), float(geo_location[1]))
        print(stations)

        return single_line_message("Hmm! I am learning how to do that. Give me a few days")

    def confirm_geo_code_location(self, data):
        address = data['queryResult']['parameters']['address']
        lat, lon, display_name, error_text = self.reverse_geocode(address)
        if error_text:
            return geocode_failure_reply()
        else:
            return confirm_geo_code_location(display_name=display_name)

    def handle_aqi_request_v2(self, data):
        self.was_request_success = False
        address = get_address_from_dialogflow(data)
        lat, lon, display_name, error_text = self.reverse_geocode(address)
        aqi_token = os.environ.get('AQI_TOKEN', '').strip()
        aqi_fetcher = AirQualityFetcher(aqi_token=aqi_token)
        fullfillment_text = ""
        if not error_text:
            aqi_results = aqi_fetcher.get_by_distance(lat, lon, results=5)
            print(aqi_results)
            print(len(aqi_results))
            if len(aqi_results) >= 1:
                self.was_request_success = True
                self.save_aqi_request_to_log(location_name=address, data=data)
                return multiple_stations_slider_report_stations(aqi_results)

        if not self.was_request_success:
            fullfillment_text = single_line_message(
                message="No nearby stations found! 😶 at {}. Try another address ".format(address))
            fullfillment_text["outputContexts"] = [{
                "name": "{}/contexts/data-upsell-yes".format(data['session']),
                "lifespanCount": 1,
                "parameters": {
                    "aqi": "no",
                }
            }]
        return fullfillment_text

    def handleMaskQuery(self, data):
        address = data.get('queryResult').get('parameters').get('address')
        geo_location = self.reverse_geocode(address)
        aqi = getNearestAQI(
            float(geo_location[0]), float(geo_location[1]))
        if aqi:
            aqi['query'] = address
            aqi['message'] = self.get_aqi_message(float(aqi['aqi']))
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

    def welcome_message(self, data):
        platform_id = data['originalDetectIntentRequest']['payload']['data']['sender']['id']
        print(platform_id)
        name = None
        try:
            user = User.objects.get(platform_id=platform_id)
            name = user.full_name
            try:
                first_name = name.split(" ")[0]
                name = first_name
            except:
                pass
        except:
            platform, platform_id, full_name = self.load_user_data_from_fb(data)
            user, created = User.objects.get_or_create(
                platform=platform,
                platform_id=platform_id,
                full_name=full_name
            )

        return welcome_message(name, user)

    def daily_subscribe_v2(self, data):
        platform, platform_id, name = self.load_user_data_from_fb(data)
        address = get_value_from_dialogflow_context(data, DIALOGFLOW_ADDRESS)
        time_period = get_value_from_dialogflow_context(data, DIALOGFLOW_TIME_PERIOD)
        start_time = time_period.get(DIALOGFLOW_TIME_PERIOD_START)
        end_time = time_period.get(DIALOGFLOW_TIME_PERIOD_END)
        start_time = parse_datetime(start_time).time()
        end_time = parse_datetime(end_time).time()
        geo_location = self.reverse_geocode(address)

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
            start_time=start_time,
            end_time=end_time,
        )
        return subscription_success_message(address)

    def handleSubscribeRequest(self, data):
        platform, platform_id, name = self.load_user_data_from_fb(data)
        address = data['queryResult']['parameters']["address"]
        geo_location = self.reverse_geocode(address)

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

        message = self.get_aqi_message(aqi)
        message = message['health']
        return single_line_message(message)

    def post(self, request):
        try:
            data = request.data
            intent = data['queryResult']['intent']['displayName']
            print(intent)
            if intent == "request.aqi":
                message = self.confirm_geo_code_location(data)
            elif intent == "request.aqi - address - confirmed" or intent == "aqi.location":
                message = self.handle_aqi_request_v2(data)
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
            elif intent == "aqi.summary.request":
                message = self.handleAQISummaryReport(data)
            elif intent == "daily.subscribe - yes":
                message = self.daily_subscribe_v2(data)
            elif intent == "Default Welcome Intent":
                message = self.welcome_message(data)
            else:
                raise Exception("Not supported")
            return Response(data=message)
        except:
            print(traceback.format_exc())
            return Response(data=single_line_message("No data avaliable"))


def aqi_detail(request):
    if request.method == "GET":
        station_id = request.GET.get('id', '')
        args = {}
        args['station_id'] = station_id
        return render(request, 'subscriptions/aqi-detail.html', args)


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
