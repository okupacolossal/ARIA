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

        # Draw path edges on top so they are clearly separated from normal roads.
        if isinstance(self.path, dict):
            for node, parent in self.path.items():
                if node in self.nodes and parent in self.nodes:
                    x1, y1 = self.nodes[parent]
                    x2, y2 = self.nodes[node]
                    pygame.draw.line(self.screen, (255, 0, 0), (x1, y1), (x2, y2), 3)
        elif isinstance(self.path, list):
            # Exact path format: [node_a, node_b, node_c, ...]
            cleaned_nodes = [node for node in self.path if node in self.nodes]
            if len(cleaned_nodes) >= 2:
                for i in range(len(cleaned_nodes) - 1):
                    u = cleaned_nodes[i]
                    v = cleaned_nodes[i + 1]
                    x1, y1 = self.nodes[u]
                    x2, y2 = self.nodes[v]
                    pygame.draw.line(self.screen, (255, 0, 0), (x1, y1), (x2, y2), 3)
            else:
                # Fallback format: [(u, v), (v, w), ...]
                for edge in self.path:
                    if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                        u, v = edge[0], edge[1]
                        if u in self.nodes and v in self.nodes:
                            x1, y1 = self.nodes[u]
                            x2, y2 = self.nodes[v]
                            pygame.draw.line(self.screen, (255, 0, 0), (x1, y1), (x2, y2), 3)


             
        
