import pygame
import random
from helpers import Helpers as hlp
import heapq

class Entities:
    def __init__(self, map, pf):
        self.map = map
        self.sprites = self._load_sprites()
        self.pathfinding = pf

        self.hospitals = []
        self.hospitals.append(Hospital("Hospital Santa Maria", 41.1600076, -8.6095796, pf))

        self.people = []

        self.entities = {
            "hospitals": self.hospitals,
            "people": self.people,
        }

    def _load_sprite(self, path: str, size: tuple[int, int]) -> pygame.Surface:
        sprite = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(sprite, size)

    def _load_sprites(self) -> dict[str, pygame.Surface]:
        return {
            "hospital": self._load_sprite("images/hospital.png", (22, 22)),
            "person": self._load_sprite("images/person.png", (16, 16)),
        }
 
    def _draw_sprite_at_geo(self, screen, sprite: pygame.Surface, latitude: float, longitude: float, map):
        x, y = hlp.transform_coordinates(
            latitude,
            longitude,
            map.min_latitude,
            map.max_latitude,
            map.min_longitude,
            map.max_longitude,
        )
        rect = sprite.get_rect(center=(x, y))
        screen.blit(sprite, rect)

    def draw(self, screen, map):
        for hospital in self.entities["hospitals"]:
            self._draw_sprite_at_geo(
                screen,
                self.sprites["hospital"],
                hospital.x,
                hospital.y,
                map,
            )

        for person in self.entities["people"]:
            self._draw_sprite_at_geo(
                screen,
                self.sprites["person"],
                person.x,
                person.y,
                map,
            )
    
    def update(self):
        for hospital in self.entities["hospitals"]:
            hospital.update(self.entities["people"])
class Hospital:
    def __init__(self, name, x, y, pf):
        self.name = name
        self.x = x
        self.y = y
        self.pathfinding = pf
        self.pursuit = False
    
    def analyze_surroundings(self, people): 

        if self.pursuit:
            return

        list_of_people = []
        for person in people:

            if person.rescuer:
                continue  # Skip if the person is already being rescued

            heapq.heappush(list_of_people, (hlp.get_distance(self.x, self.y, person.x, person.y), person))

        closest = heapq.heappop(list_of_people)[1] if list_of_people else None

        self.map.path = self.pathfinding.run_astar(self, closest) if closest else None

        self.pursuit = True


             
        

    def update(self, people):
        self.analyze_surroundings(people)
    


class Person:
    def __init__(self, name, x, y, timer_seconds: float = 30.0, spawn_time: float = 0.0):
        self.name = name
        self.x = x
        self.y = y
        self.timer_seconds = timer_seconds
        self.spawn_time = spawn_time
        self.rescuer = None

    @classmethod
    def create_random(
        cls,
        name: str,
        map,
        edge_margin_ratio: float = 0.05,
        timer_seconds: float = 30.0,
        spawn_time: float = 0.0,
    ):
        latitude_range = map.max_latitude - map.min_latitude
        longitude_range = map.max_longitude - map.min_longitude

        lat_margin = latitude_range * edge_margin_ratio
        lon_margin = longitude_range * edge_margin_ratio

        random_latitude = random.uniform(map.min_latitude + lat_margin, map.max_latitude - lat_margin)
        random_longitude = random.uniform(map.min_longitude + lon_margin, map.max_longitude - lon_margin)

        return cls(name, random_latitude, random_longitude, timer_seconds=timer_seconds, spawn_time=spawn_time)

    def is_alive(self, now_seconds: float) -> bool:
        return (now_seconds - self.spawn_time) < self.timer_seconds