import random
import math

class Helpers:
    @staticmethod

    def get_random_passable(grid):
        all_cells = [cell for column in grid.cells for cell in column]
        passable_cells = [cell for cell in all_cells if cell is not None and cell.passable]
        return random.choice(passable_cells) if passable_cells else None
    
    def get_distance(start, goal):
        return math.sqrt((start.x - goal.x)**2 + (start.y - goal.y)**2)