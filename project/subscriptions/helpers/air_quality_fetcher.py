import json
import os
import random
import traceback

import geopy.distance
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


def distance(lat1, lon1, lat2, lon2):
    coords_1 = (lon1, lat1)
    coords_2 = (lon2, lat2)
    return geopy.distance.vincenty(coords_1, coords_2).km


class AirQualityInfo:

    def __init__(self):
        self.aqi_token = os.environ.get('AQI_TOKEN', '')

    def getNearestAQI(self, lat, lon):
        url = "https://api.waqi.info/map/bounds/?token={}&latlng=26.3978980576,80.0884245137,30.4227169866,88.1748043151".format(
            self.aqi_token)
        response = requests.get(url)
        stations = json.loads(response.text)['data']
        print("Found {} stations".format(len(stations)))

        for station in stations:
            station['distance'] = distance(
                lat, lon, station["lat"], station["lon"])
        stations.sort(key=lambda x: (x["distance"]))

        return stations[0]
