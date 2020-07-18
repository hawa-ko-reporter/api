import json
import os

import requests

from .geo import distance


def getNearestAQI(lat, lon):
    aqi_token = os.environ.get('AQI_TOKEN', '').strip()
    print(aqi_token)
    url = "https://api.waqi.info/map/bounds/?token={}&latlng=26.3978980576,80.0884245137,30.4227169866,88.1748043151".format(
        aqi_token)
    response = requests.get(url)
    stations = json.loads(response.text)['data']

    print("Found {} stations".format(len(stations)))

    for station in stations:
        print(lat, lon, station["lat"], station["lon"])
        station['distance'] = distance(
            lat, lon, float(station["lat"]), float(station["lon"]))
    stations.sort(key=lambda x: (x["distance"]))
    return stations[0]


def aqi_level(aqi):
    aqi = int(aqi)
    if aqi <= 50:
        return {"level": "Good", }
    elif aqi <= 100:
        return {"level": "Moderate", }
    elif aqi <= 150:
        return {"level": "Unhealthy for Sensitive Groups", }
    elif aqi <= 200:
        return {"level": "Unhealthy", },
    elif aqi <= 300:
        return {"level": "Very Unhealthy", }
    elif aqi > 300:
        return {"level": "Hazardous", }
    else:
        return {}


def prepare_aqi_message(data):
    aqi = data['aqi']
    station_name = data['station']['name']
    level = aqi_level(aqi=aqi)['level']
    messages = ["The AQI from the nearest station at {} is {} at {}".format(station_name, level, aqi),
                ]
    return messages


class AirQualityFetcher:
    url = "https://api.waqi.info/map/bounds/?token={}&latlng=26.3978980576,80.0884245137,30.4227169866,88.1748043151"
    response_text = None

    def __init__(self, aqi_token):
        self.url = self.url.format(aqi_token)

    def map_data(self):
        stations = json.loads(self.response_text)['data']
        return stations

    def get_aqi(self):
        response = requests.get(self.url)
        self.response_text = response.text

    def get_by_station_id(self, station_id):
        self.get_aqi()
        stations = self.map_data()
        station = next(x for x in stations if x["uid"] == station_id)
        return station

    def get_by_nearest_location(self, lat, lon):
        pass
