import pygame
from helpers import Helpers as hlp


class Entities:
    def __init__(self, map):
        self.map = map
        self.sprites = self._load_sprites()

        self.hospitals = []
        self.hospitals.append(Hospital("Hospital Santa Maria", 41.1600076, -8.6095796))

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

class Hospital:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y


class Person:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y