import pygame
import constants
import os
from ui.hud import RetroHud
import generations
import entities

class Game:
    def __init__(self): 

        # HOSPITALS
        self.hospital_image = None
        self.hospital_size = 24
        self.stations = []


        # PEOPLE

        self.person_image = None
        self.person_size = 14
        self.people = []

        # TIME

        self.start_tick = pygame.time.get_ticks()
        self.people_tick = pygame.time.get_ticks()
        self.current_tick = self.start_tick

        # LOAD
        self._load_hospital_sprite()
        self._load_person_sprite()
        self.generations_handler = generations.Generations()

        self.hud = RetroHud(self)


    def add_station(self, station):
        self.stations.append(station)

    def add_person(self, person):
        self.people.append(person)

    def update(self):
        self.current_tick = pygame.time.get_ticks()
        elapsed = self.current_tick - self.start_tick
        people_timer = self.current_tick - self.people_tick
        
        if elapsed >= self.generations_handler.generation_interval * 1000:
            self.generations_handler.current_generation += 1
            self.start_tick = self.current_tick

        if people_timer >= self.generations_handler.person_spawn_interval * 1000:
            self.people_tick = self.current_tick
            entities.Person(self.stations[0].closest_passable)
          

    def draw(self, grid, screen):
        for road in grid.roads.values():
            p1 = (road.cell1.x, road.cell1.y)
            p2 = (road.cell2.x, road.cell2.y)

            if road.width >= 3:
                pygame.draw.line(screen, (108, 114, 122), p1, p2, road.width)
            else:
                pygame.draw.line(screen, (78, 84, 92), p1, p2, road.width)

        for cell in grid.cells:
            for c in cell:
                if c is not None:
                    pygame.draw.circle(screen, c.color, (c.x, c.y), grid.cell_radius)

        for station in self.stations:
            if self.hospital_image is not None:
                rect = self.hospital_image.get_rect(center=(station.location.x, station.location.y))
                screen.blit(self.hospital_image, rect)
            else:
                pygame.draw.circle(screen, constants.BLUE, (station.location.x, station.location.y), 8)

        for person in self.people:
            if self.person_image is not None:
                rect = self.person_image.get_rect(center=(person.location.x, person.location.y))
                screen.blit(self.person_image, rect)
            else:
                pygame.draw.circle(screen, person.color, (person.location.x, person.location.y), person.radius)

        alive_people = sum(1 for person in self.people if getattr(person, "lifetime", 1) > 0)
        self.hud.draw(screen, alive_people=alive_people, total_people=len(self.people))

    def _load_hospital_sprite(self):
        image_path = os.path.join(os.path.dirname(__file__), "images", "hospital.png")
        try:
            image = pygame.image.load(image_path).convert_alpha()
            self.hospital_image = pygame.transform.smoothscale(image, (self.hospital_size, self.hospital_size))
        except (pygame.error, FileNotFoundError):
            self.hospital_image = None

    def _load_person_sprite(self):
        image_path = os.path.join(os.path.dirname(__file__), "images", "person.png")
        try:
            image = pygame.image.load(image_path).convert_alpha()
            self.person_image = pygame.transform.smoothscale(image, (self.person_size, self.person_size))
        except (pygame.error, FileNotFoundError):
            self.person_image = None