import geopy.distance


def distance(lat1, lon1, lat2, lon2):
    coords_1 = (lon1, lat1)
    coords_2 = (lon2, lat2)
    return geopy.distance.geodesic(coords_1, coords_2).km
