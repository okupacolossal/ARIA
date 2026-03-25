from helpers import Helpers as hlp
class Pathfinding:
    def __init__(self, map, entities):
        self.map = map
        self.entities = entities
    
    def get_cell_from_click(self, click_pos):
        for node_id, (x, y) in self.map.nodes.items():
            if (x - click_pos[0]) ** 2 + (y - click_pos[1]) ** 2 < 100:  # 10 pixels radius
                closest_hospital = self.entities.entities["hospitals"][0]  # Assuming you want to start from the first hospital
                self.run_astar(hlp.get_closest_node(closest_hospital.x, closest_hospital.y, self.map), goal=node_id)  # You can set a goal node here
        print("Clicked on no node")
        return None


    def run_astar(self, start, goal):
        print('Running A* algorithm from', start, 'to', goal) 
        neighbours = self.map.G.neighbors(start)
        print('Neighbours of start node:', list(neighbours))
    
    