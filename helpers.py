import settings

class Helpers:
    @staticmethod
    def transform_coordinates(lat, lan, min_latitude, max_latitude, min_longitude, max_longitude):
        x = int((lan - min_longitude) / (max_longitude - min_longitude) * settings.SCREEN_WIDTH)
        y = int((1 -(lat - min_latitude) / (max_latitude - min_latitude)) * settings.SCREEN_HEIGHT)
        return (x, y)
    
    @staticmethod
    def get_closest_node(latitude, longitude, map):
        closest_node = None
        min_distance = float('inf')
        for node_id, (x, y) in map.nodes.items():
            distance = ((x - longitude) ** 2 + (y - latitude) ** 2) ** 0.5
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