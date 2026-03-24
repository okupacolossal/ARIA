import osmnx as ox
import settings
import pygame

class Map():
    
    def __init__(self):
       self.map = self.get_map()

    def get_map(self):
        place_name = "Porto, Portugal"
        G = ox.graph_from_place(place_name, network_type="drive")
        print(G)