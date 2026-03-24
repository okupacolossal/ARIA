import osmnx as ox
from settings import *
import pygame
import os
from helpers import Helpers as hlp

class Map():
    
    def __init__(self, screen):
         self.screen = screen
         self.nodes = self.get_map()

    def get_map(self):
         
        if os.path.exists("porto_map.graphml"):
            self.G = ox.load_graphml("porto_map.graphml")
        else:
            center = (41.1579, -8.6291)  # Porto city center 
            self.G = ox.graph_from_point(center, dist=5000, network_type="drive")  
            ox.save_graphml(self.G, "porto_map.graphml")
        
        self.latitudes = []
        self.longitudes = []
 
        screen_nodes = {}
        
        for _, data in self.G.nodes(data=True):
            self.latitudes.append(data['y'])
            self.longitudes.append(data['x'])
        
        self.min_latitude = min(self.latitudes)
        self.max_latitude = max(self.latitudes)
        self.min_longitude = min(self.longitudes)
        self.max_longitude = max(self.longitudes)

        for node, data in self.G.nodes(data=True):
            x, y = hlp.transform_coordinates(
                data['y'], data['x'], 
                self.min_latitude, self.max_latitude, 
                self.min_longitude, self.max_longitude
            )
            screen_nodes[node] = (x, y)

        return screen_nodes


    def draw(self):
        for u, v, data in self.G.edges(data=True):
            x1, y1 = self.nodes[u]
            x2, y2 = self.nodes[v]
            pygame.draw.line(self.screen, (60, 60, 60), (x1, y1), (x2, y2), 1)


             
        
