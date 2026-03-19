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
                if n[0] >= 0 and n[0] < grid.width and n[1] >= 0 and n[1] < grid.height:
                    neighbours.append(grid.cells[n[0]][n[1]])
            
            return neighbours
            
        
        g_score = {'start': 0}  
        estimated_cost = hlp.get_distance(start, goal)
        open_list = []
        closed_set = set()

        ns = get_neighbours(start)
        print(ns)

        

            
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
                
     
        


    def get_clicked_cell(self, mouse_pos, grid):
        mouse_x, mouse_y = mouse_pos
        search_radius = max(5, grid.cell_size // 2)

        for column in grid.cells:
            for cell in column:
                if cell is None:
                    continue
                if abs(cell.x - mouse_x) <= search_radius and abs(cell.y - mouse_y) <= search_radius:
                    return cell

        return None

    def test_path_from_station_click(self, station, mouse_pos, grid):
        selected_cell = self.get_clicked_cell(mouse_pos, grid)
        if selected_cell is None:
            return None

        self.selected_cell = selected_cell
        start_cell = getattr(station, "closest_passable", station.location)
        self.last_test_path = self.astar(start_cell, selected_cell, grid)
        return selected_cell