import osmnx as ox
from settings import *
import pygame
import os

class Map():
    
    def __init__(self, screen):
         self.screen = screen
         self.nodes = self.get_map()

    def get_map(self):
         
        if os.path.exists("porto_map.graphml"):
            self.G = ox.load_graphml("porto_map.graphml")
        else:
            center = (41.1579, -8.6291)  # Porto city center 
            self.G = ox.graph_from_point(center, dist=1500, network_type="drive")  
            ox.save_graphml(self.G, "porto_map.graphml")
        
        latitudes = []
        longitudes = []
 
        screen_nodes = {}
        
        for _, data in self.G.nodes(data=True):
            latitudes.append(data['y'])
            longitudes.append(data['x'])
        
        min_latitude = min(latitudes)
        max_latitude = max(latitudes)
        min_longitude = min(longitudes)
        max_longitude = max(longitudes)

        for node, data in self.G.nodes(data=True):
            x = int((data['x'] - min_longitude) / (max_longitude - min_longitude) * SCREEN_WIDTH)
            y = int((1 -(data['y'] - min_latitude) / (max_latitude - min_latitude)) * SCREEN_HEIGHT)
            screen_nodes[node] = (x, y)

        return screen_nodes


    def draw(self):
        for u, v, data in self.G.edges(data=True):
            x1, y1 = self.nodes[u]
            x2, y2 = self.nodes[v]
            pygame.draw.line(self.screen, (60, 60, 60), (x1, y1), (x2, y2), 1)


             
        
