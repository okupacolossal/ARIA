import osmnx as ox
from settings import *
import pygame
import os
from helpers import Helpers as hlp

class Map():
    
    def __init__(self, screen):
         self.screen = screen
         self.nodes = self.get_map()
         self.path = []

    def get_map(self):
         
        if os.path.exists("porto_map.graphml"):
            self.G = ox.load_graphml("porto_map.graphml")
        else:
            center = (41.14961, -8.61099)  # Porto city center 
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
            screen_x, screen_y = hlp.transform_coordinates(
                data['y'], data['x'], 
                self.min_latitude, self.max_latitude, 
                self.min_longitude, self.max_longitude
            )
            screen_nodes[node] = (screen_x, screen_y)

        for _, _, data in self.G.edges(data=True):
            edge_length = float(data.get("length", 40.0))
            intensity = max(0.0, min(1.0, edge_length / 220.0))
            base_green = 64 + int(20 * intensity)
            data['glow_color'] = (18, base_green - 14, 18)
            data['base_color'] = (24, base_green, 24)
            data['core_color'] = (32, base_green + 10, 32)
            data['thickness_glow'] = 3 if intensity > 0.7 else 2
            data['thickness_base'] = 1
            data['thickness_core'] = 1


        return screen_nodes


    def draw(self):
        for u, v, data in self.G.edges(data=True):
            x1, y1 = self.nodes[u]
            x2, y2 = self.nodes[v]
            pygame.draw.line(self.screen, data['glow_color'], (x1, y1), (x2, y2), data['thickness_glow'])
            pygame.draw.line(self.screen, data['base_color'], (x1, y1), (x2, y2), data['thickness_base'])
            pygame.draw.line(self.screen, data['core_color'], (x1, y1), (x2, y2), data['thickness_core'])

             
        
