from helpers import Helpers as hlp
import heapq
import osmnx as ox

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

        return path
    
    def run_astar(self, start, goal):

        print('Running A* algorithm from', start, 'to', goal) 

        def heuristic(node1, node2):
            x1, y1 = self.map.nodes[node1]
            x2, y2 = self.map.nodes[node2]
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        # init lists
        counter = 0

        closed_set = set()
        open_list = []
        counter = 0
        came_from = {start: None}
        initial_heuristic = heuristic(start, goal)
        g_score = {start: 0}
        

        # initial heap push
        heapq.heappush(open_list, (g_score[start] + initial_heuristic, counter, start))  # (f_score, node)

        while open_list:
            f, _, current = heapq.heappop(open_list)  # Get the node with the lowest f_score

            counter += 1

            if current == goal:
                return self.reconstruct_path(came_from, current)
            
            closed_set.add(current)

            for _, neighbor, _, data in self.map.G.edges(current, keys=True, data=True):
    
                if neighbor in closed_set:
                    continue

                edge_length = data.get("length", 1)
                tentative_g = g_score[current] + edge_length
                heur = heuristic(neighbor, goal)
                f_score = tentative_g + heur
                counter += 1

                heapq.heappush(open_list, (f_score, counter, neighbor))

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    came_from[neighbor] = current

        return came_from
    
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
         

  
        
    
    