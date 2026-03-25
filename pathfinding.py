from helpers import Helpers as hlp
import heapq

class Pathfinding:
    def __init__(self, map, entities):
        self.map = map
        self.entities = entities
    
    def get_cell_from_click(self, click_pos):
        for node_id, (x, y) in self.map.nodes.items():
            if (x - click_pos[0]) ** 2 + (y - click_pos[1]) ** 2 < 100:  # 10 pixels radius
                closest_hospital = self.entities.entities["hospitals"][0]  # Assuming you want to start from the first hospital
                hospital_screen_x, hospital_screen_y = hlp.transform_coordinates(
                    closest_hospital.x,
                    closest_hospital.y,
                    self.map.min_latitude,
                    self.map.max_latitude,
                    self.map.min_longitude,
                    self.map.max_longitude,
                )
                self.map.path = self.run_astar(
                    hlp.get_closest_node(hospital_screen_y, hospital_screen_x, self.map),
                    goal=node_id,
                )  # You can set a goal node here
                return
        return None
    
    def reconstruct_path(self, came_from, current):

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



        
    
    