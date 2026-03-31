from helpers import Helpers as hlp
import heapq
import osmnx as ox
import networkx as nx

class Pathfinding:
    def __init__(self, map):
        self.map = map
    
    @staticmethod
    def reconstruct_path(came_from, current):

        path = [current]
        
        while current in came_from:

            current = came_from[current]
            path.append(current)
        
        path = path[::-1]  # Reverse the path
        path.remove(None)  # Remove the None entry if it exists

        return path
    
    def run_astar(self, start, goal):

        def heuristic(node1, node2):
            x1, y1 = self.map.nodes[node1]
            x2, y2 = self.map.nodes[node2]
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        try:
            return nx.astar_path(self.map.G, start, goal, heuristic=heuristic, weight="length")
        except nx.NetworkXNoPath:
            return [start, goal]
    
    def get_closest_cell(self, longitude, latitude): 
        try:
            return ox.nearest_nodes(self.map.G, X=longitude, Y=latitude)
        except ImportError:
            # Fallback for unprojected graphs when scikit-learn is unavailable.
            closest_node = None
            min_distance_sq = float("inf")
            for node_id, data in self.map.G.nodes(data=True):
                node_longitude = data.get("x")
                node_latitude = data.get("y")
                if node_longitude is None or node_latitude is None:
                    continue

                dx = node_longitude - longitude
                dy = node_latitude - latitude
                distance_sq = dx * dx + dy * dy
                if distance_sq < min_distance_sq:
                    min_distance_sq = distance_sq
                    closest_node = node_id

            if closest_node is None:
                raise RuntimeError("No graph nodes available for nearest-node lookup.")
            return closest_node
         

  
        
    
    