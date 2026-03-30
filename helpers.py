import math

from matplotlib.pylab import angle

import settings

class Helpers:
    @staticmethod
    def transform_coordinates(latitude, longitude, min_latitude, max_latitude, min_longitude, max_longitude):
        screen_x = int((longitude - min_longitude) / (max_longitude - min_longitude) * settings.SCREEN_WIDTH)
        screen_y = int((1 - (latitude - min_latitude) / (max_latitude - min_latitude)) * settings.SCREEN_HEIGHT)
        return (screen_x, screen_y)
    
    @staticmethod
    def get_closest_node(latitude, longitude, map):
        closest_node = None
        min_distance = float('inf')
        for node_id, (screen_x, screen_y) in map.nodes.items():
            distance = ((screen_x - longitude) ** 2 + (screen_y - latitude) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_node = node_id
        return closest_node
    
    @staticmethod
    def get_distance(lat1, lon1, lat2, lon2):
        # Haversine formula to calculate distance between two lat/lon points
        from math import radians, cos, sin, sqrt, atan2

        R = 6371  # Earth radius in kilometers

        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        return distance
    
    @staticmethod
    def get_direction(lat1, lon1, lat2, lon2):
        d_lon = lon2 - lon1
        d_lat = lat2 - lat1
        # Use 0 deg at +longitude (east), increasing counter-clockwise,
        # to match get_normalized_lonlan(cos, sin) below.
        angle = (math.degrees(math.atan2(d_lat, d_lon)) + 360) % 360
        return angle
    
    @staticmethod
    def get_normalized_lonlan(direction):
        # Convert angle to a unit vector
        radians = math.radians(direction)
        lon = math.cos(radians)
        lat = math.sin(radians)
        return (lon, lat)