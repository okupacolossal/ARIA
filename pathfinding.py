import heapq
import math

class Pathfinder:
    def __init__(self, grid):
        self.grid = grid
        self.selected_cell = None

    def astar(self, start, goal):

        cells = self.grid.cells

        open_list = []
        closed_set = set()
    
        initial_distance_to_goal = math.sqrt((start.x - goal.x)**2 + (start.y - goal.y)**2)
        counter = 0
        heapq.heappush(open_list, (initial_distance_to_goal, counter, start))

        came_from = {}
        came_from[start.i, start.j] = None  # Start node has no parent

        while open_list:
            f, _,  node = heapq.heappop(open_list)
            
            node_i, node_j = node.i, node.j

            if node_i == goal.i and node_j == goal.j:
                break

            if (node_i, node_j) in closed_set:
                continue

            closed_set.add((node_i, node_j))
            neighbours = []
            
            if node_i + 1 < self.grid.width:
                neighbours.append(self.grid.cells[node_i + 1][node_j])
            if node_i - 1 >= 0:
                neighbours.append(self.grid.cells[node_i - 1][node_j])
            if node_j - 1 >= 0:
                neighbours.append(self.grid.cells[node_i][node_j - 1])
            if node_j + 1 < self.grid.height:
                neighbours.append(self.grid.cells[node_i][node_j + 1])
    
            for n in neighbours:
                if n:
                    g = math.sqrt((start.x - n.x)**2 + (start.y - n.y)**2)
                    h = math.sqrt((n.x - goal.x)**2 + (n.y - goal.y)**2)
                    f = g + h
                    heapq.heappush(open_list, (f, counter, n))
                    counter += 1

                    if (n.i, n.j) not in came_from:  # Only set the parent if it hasn't been set before~
                        came_from[n.i, n.j] = (node_i, node_j)  # Store the parent of the neighbor


        current = (goal.i, goal.j)
        while current is not None and current in came_from:
            self.grid.cells[current[0]][current[1]].color = (255, 0, 0)  # Mark the path in red
            current = came_from[current]
                
            





    def cell_click(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        for i in self.grid.cells:
            for cell in i:
                if cell is not None and cell.x <= mouse_x + 5 and cell.x >= mouse_x - 5 and cell.y <= mouse_y + 5 and cell.y >= mouse_y - 5:
                    selected_cell = cell

                    astar_result = self.astar(self.grid.cells[13][13], selected_cell)  # Example: path from center to clicked cell
                    return cell