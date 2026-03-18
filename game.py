import pygame
import constants

class Game:
    def __init__(self): 
        self.stations = []

    def add_station(self, station):
        self.stations.append(station)

    def update(self):
        pass

    def draw(self, grid, screen):
        
        for road in grid.roads.values():
            pygame.draw.line(screen, road.color, (road.cell1.x, road.cell1.y), (road.cell2.x, road.cell2.y), road.width)

        for cell in grid.cells:
            for c in cell:
                if c is not None:
                    pygame.draw.circle(screen, c.color, (c.x, c.y), grid.cell_radius)

        for station in self.stations:
            pygame.draw.circle(screen, constants.BLUE, (station.location.x, station.location.y), 5)