import constants
import pygame
from helpers import Helpers as hlp
class Station:
    def __init__(self, location, grid, pathfinder, game):
        self.location = location
        self.grid = grid 
        self.game = game
        location.passable = False
        self.x = location.x
        self.y = location.y
        self.i = location.i
        self.j = location.j
        self.color = constants.BLUE
        self.closest_passable = pathfinder.get_closest_passable(self.location, self.grid)

        #amb

        self.max_ambulances = 2
        self.ambulances = []
        
        # stats

        self.radius = 1000
    
    def check_for_people(self):

        for person in self.game.people:
            if hlp.get_distance(self, person) < self.radius:
                pass
        
    def update(self):
        self.check_for_people()
class Person:
    def __init__(self, location, game):
        self.location = location
        self.game = game
        self.i = location.i
        self.j = location.j
        self.x = location.x
        self.y = location.y
        self.color = constants.BLUE
        self.lifetime = 6
        self.spawn_tick = pygame.time.get_ticks()

    def update(self):
        elapsed = (pygame.time.get_ticks() - self.spawn_tick) / 1000
        if elapsed >= self.lifetime:
            self.lifetime = 0
            self.game.people.remove(self)
class Ambulance:
    def __init__(self, station):
        self.station = station
        self.location = station.location
        self.destination = None
        self.path = []