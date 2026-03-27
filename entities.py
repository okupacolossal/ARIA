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
        self.hospitals.append(Hospital("Hospital Santa Maria", -8.6095796, 41.1600076, pf))

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
 
    def _draw_sprite_at_geo(self, screen, sprite: pygame.Surface, longitude: float, latitude: float, map):
        screen_x, screen_y = hlp.transform_coordinates(
            latitude,
            longitude,
            map.min_latitude,
            map.max_latitude,
            map.min_longitude,
            map.max_longitude,
        )
        rect = sprite.get_rect(center=(screen_x, screen_y))
        screen.blit(sprite, rect)

    def draw(self, screen, map):
        for hospital in self.entities["hospitals"]:
            self._draw_sprite_at_geo(
                screen,
                self.sprites["hospital"],
                hospital.longitude,
                hospital.latitude,
                map,
            )

        for person in self.entities["people"]:
            self._draw_sprite_at_geo(
                screen,
                self.sprites["person"],
                person.longitude,
                person.latitude,
                map,
            )
    
    def update(self, now_seconds: float):
        for hospital in self.entities["hospitals"]:
            hospital.update(self.people, now_seconds)


class Hospital:
    def __init__(self, name, longitude, latitude, pf):
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.pathfinding = pf
        self.map = pf.map
        
        self.pursuit = False
        self.scan_interval_seconds = 1.0
        self.last_scan_seconds = -self.scan_interval_seconds

        self.closest_cell = self.pathfinding.get_closest_cell(self.longitude, self.latitude)
    
    def analyze_surroundings(self, people): 

        list_of_people = []
        for person in people:

            if person.rescuer:
                continue  # Skip if the person is already being rescued

            
            distance = hlp.get_distance(
                self.latitude,
                self.longitude,
                person.latitude,
                person.longitude,
            )

            heapq.heappush(list_of_people, (distance, person))

        closest = heapq.heappop(list_of_people)[1] if list_of_people else None
        if closest is None:
            return

        if closest.closest_cell is None:
            closest.closest_cell = self.pathfinding.get_closest_cell(
                closest.longitude,
                closest.latitude,
            )

        path = self.pathfinding.run_astar(self.closest_cell, closest.closest_cell)
        
        if path:
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                self.map.G.edges[u, v, 0]['color'] = (122, 30, 30)
                self.map.G.edges[u, v, 0]['thickness'] = 3


             
        

    def update(self, people, now_seconds: float):
        if self.pursuit:
            return

        if (now_seconds - self.last_scan_seconds) < self.scan_interval_seconds:
            return

        self.last_scan_seconds = now_seconds
        self.analyze_surroundings(people)
    


class Person:
    def __init__(self, name, longitude, latitude, timer_seconds: float = 30.0, spawn_time: float = 0.0, pf=None):
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.timer_seconds = timer_seconds
        self.spawn_time = spawn_time
        self.rescuer = None
        self.pf = pf

        self.closest_cell = None

    @classmethod
    def create_random(
        cls,
        name: str,
        map,
        edge_margin_ratio: float = 0.05,
        timer_seconds: float = 30.0,
        spawn_time: float = 0.0,
        pf = None,
    ):
        latitude_range = map.max_latitude - map.min_latitude
        longitude_range = map.max_longitude - map.min_longitude

        lat_margin = latitude_range * edge_margin_ratio
        lon_margin = longitude_range * edge_margin_ratio

        random_latitude = random.uniform(map.min_latitude + lat_margin, map.max_latitude - lat_margin)
        random_longitude = random.uniform(map.min_longitude + lon_margin, map.max_longitude - lon_margin)

        return cls(
            name,
            random_longitude,
            random_latitude,
            timer_seconds=timer_seconds,
            spawn_time=spawn_time,
            pf=pf,
        )

    def is_alive(self, now_seconds: float) -> bool:
        return (now_seconds - self.spawn_time) < self.timer_seconds