import settings

class Helpers:
    @staticmethod
    def transform_coordinates(lat, lan, min_latitude, max_latitude, min_longitude, max_longitude):
        x = int((lan - min_longitude) / (max_longitude - min_longitude) * settings.SCREEN_WIDTH)
        y = int((1 -(lat - min_latitude) / (max_latitude - min_latitude)) * settings.SCREEN_HEIGHT)
        return (x, y)
    
    @staticmethod
    def get_closest_node(self, latitude, longitude, map):
        closest_node = None
        min_distance = float('inf')
        for node_id, (x, y) in map.nodes.items():
            distance = ((x - longitude) ** 2 + (y - latitude) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_node = node_id
        return closest_node