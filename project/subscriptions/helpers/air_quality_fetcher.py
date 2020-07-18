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
