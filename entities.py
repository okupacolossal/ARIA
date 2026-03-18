import constants
class Station:
    def __init__(self, location, grid, pathfinder):
        self.location = location
        self.grid = grid
        location.passable = False
        self.x = location.x
        self.y = location.y
        self.i = location.i
        self.j = location.j
        self.color = constants.BLUE
        self.closest_passable = pathfinder.get_closest_passable(self.location, self.grid)
        

class Person:
    def __init__(self, location):
        self.location = location
        self.color = constants.BLUE
        self.radius = 5

        self.lifetime = 6