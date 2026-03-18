import heapq
import math

class Pathfinder:
    def __init__(self):
        self.selected_cell = None

    def astar(self, start, goal, grid):
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
            
            if node_i + 1 < grid.width:
                neighbours.append(grid.cells[node_i + 1][node_j])
            if node_i - 1 >= 0:
                neighbours.append(grid.cells[node_i - 1][node_j])
            if node_j - 1 >= 0:
                neighbours.append(grid.cells[node_i][node_j - 1])
            if node_j + 1 < grid.height:
                neighbours.append(grid.cells[node_i][node_j + 1])
    
            for n in neighbours:
                if n and n.passable:
                    g = math.sqrt((start.x - n.x)**2 + (start.y - n.y)**2)
                    h = math.sqrt((n.x - goal.x)**2 + (n.y - goal.y)**2)
                    f = g + h
                    heapq.heappush(open_list, (f, counter, n))
                    counter += 1

                    if (n.i, n.j) not in came_from:  # Only set the parent if it hasn't been set before~
                        came_from[n.i, n.j] = (node_i, node_j)  # Store the parent of the neighbor


        current = (goal.i, goal.j)
        while current is not None and current in came_from:
            grid.cells[current[0]][current[1]].color = (255, 0, 0)  # Mark the path in red
            current = came_from[current]
                
            
    def get_closest_passable(self, cell, grid):

        open_list = [cell]
        visited = set()
        
        while open_list:   
                

                current = open_list.pop(0)

                if current in visited:
                    continue
                
                neighbours = {
                    (current.i + 1, current.j),
                    (current.i - 1, current.j),
                    (current.i, current.j - 1),
                    (current.i, current.j + 1)
                }
                
                visited.add(current)

                for n in neighbours:
                    if grid.cells[n[0]][n[1]]:
                        cell = grid.cells[n[0]][n[1]]
                        open_list.append(cell)
                        if cell.passable:
                            return cell
                
     
        


    def cell_click(self, departing_point, mouse_pos, grid):
        mouse_x, mouse_y = mouse_pos
        for i in grid.cells:
            for cell in i:
                if cell is not None and cell.x <= mouse_x + 5 and cell.x >= mouse_x - 5 and cell.y <= mouse_y + 5 and cell.y >= mouse_y - 5:
                    selected_cell = cell

                    astar_result = self.astar(departing_point, selected_cell, grid)  # Example: path from center to clicked cell
                    return cell