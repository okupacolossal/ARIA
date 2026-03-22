import heapq
import math
from helpers import Helpers as hlp

class Pathfinder:
    def __init__(self):
        self.selected_cell = None
        self.last_test_path = None

    def astar(self, start, goal, grid):

        def get_neighbours(target):
            potential_neighbours = [
            (target.i + 1, target.j),
            (target.i - 1, target.j),
            (target.i, target.j + 1),
            (target.i, target.j - 1)
            ]

            neighbours = []

            for n in potential_neighbours:
                if n[0] >= 0 and n[0] < grid.width and n[1] >= 0 and n[1] < grid.height and grid.cells[n[0]][n[1]].passable:
                    neighbours.append(grid.cells[n[0]][n[1]])
            
            return neighbours
        
        def heuristic(cell1, goal):
            return hlp.get_distance(cell1, goal)
        
        def g_func(cell1, cell2, goal):
            return hlp.get_distance(cell1, cell2)
        

    
        
        g_score = {}
        g_score[start] = 0
        estimated_cost = g_score[start] + hlp.get_distance(start, goal)
        open_list = []
        closed_set = set()
        counter = 0

        path = []

        heapq.heappush(open_list, (estimated_cost, counter, start))
        
        while open_list:

            _, _, current = heapq.heappop(open_list)
            path.append(current)

            if current == goal:
                for node in path:
                    node.color = (255, 0)
                break

            closed_set.add(current) 

            neighbours = get_neighbours(current)

            for n in neighbours:

                if n in closed_set:
                    continue

                h = heuristic(n, goal)
                g = g_score[current] + hlp.get_distance(current, n)
                f_score = g + h
                counter += 1

                if g < g_score.get(n, float('inf')):
                    g_score[n] = g
                    heapq.heappush(open_list, (f_score, counter, n))
                           
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
    
    def get_closest_cell_to_click(self, mouse_pos, grid):
        # get closest cell to mouse click
            closest_cell = None
            closest_distance = float('inf')

            mouse_pos = mouse_pos.x, mouse_pos.y

            for column in grid.cells:
                for cell in column:
                    if cell is not None:
                        distance = hlp.get_distance(cell, mouse_pos)
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_cell = cell

            return closest_cell

    def test_path_from_station_click(self, station, mouse_pos, grid):
        closest_cell = self.get_closest_cell_to_click(mouse_pos, grid)
        self.astar(station, closest_cell, grid)