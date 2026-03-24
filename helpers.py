import settings

class Helpers:
    @staticmethod
    def transform_coordinates(lat, lan, min_latitude, max_latitude, min_longitude, max_longitude):
        x = int((lan - min_longitude) / (max_longitude - min_longitude) * settings.SCREEN_WIDTH)
        y = int((1 -(lat - min_latitude) / (max_latitude - min_latitude)) * settings.SCREEN_HEIGHT)
        return (x, y)