import json
import os

import requests

from .geo import distance


def get_aqi(lat, lon, results_to_return=10):
    aqi_token = os.environ.get('AQI_TOKEN', '').strip()
    url = "https://api.waqi.info/map/bounds/?token={}&latlng=26.3978980576,80.0884245137,30.4227169866,88.1748043151".format(
        aqi_token)
    response = requests.get(url)
    stations = json.loads(response.text)['data']

    for station in stations:
        print(lat, lon, station["lat"], station["lon"])
        station['distance'] = distance(
            lat, lon, float(station["lat"]), float(station["lon"]))

    stations.sort(key=lambda x: (x["distance"]))
    return stations[0:results_to_return]


def getNearestAQI(lat, lon):
    aqi_token = os.environ.get('AQI_TOKEN', '').strip()
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

    is_station_nearby = stations[0]['distance'] < 100
    if is_station_nearby:
        return stations[0]
    else:
        return {}


def get_aqi_code(aqi):
    aqi = int(aqi)
    if aqi <= 50:
        message = 0.0, "good"
    elif aqi <= 100:
        message = 1.0, ""
    elif aqi <= 150:
        message = 2.0, ""
    elif aqi <= 200:
        message = 3.0, ""
    elif aqi <= 300:
        message = 4.0, ""
    else:
        message = 5.0, ""
    return message


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
        print(self.url)

    def map_data(self):
        stations = json.loads(self.response_text)['data']
        return stations

    def get_aqi(self):
        response = requests.get(self.url)
        self.response_text = response.text

    def get_by_distance(self, lat, lon):
        self.get_aqi()
        stations = self.map_data()

        for subs in stations:
            subs_lat = subs.get("latitude")
            subs_lon = subs.get("longitude")
            distance_in_km = distance(subs_lat, subs_lon, lat, lon)
            subs['distance'] = distance_in_km

        stations.sort(key=lambda x: (x["distance"]))
        return stations[0]

    def get_by_station_id(self, station_name):
        self.get_aqi()
        stations = self.map_data()
        selected_station = None
        for x in stations:
            current_station = x['station']['name']
            if current_station == station_name:
                selected_station = current_station

        return selected_station
