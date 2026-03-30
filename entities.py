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
        self.hospitals.append(Hospital("Hospital Santa Maria", -8.6095796, 41.1600076, pf, self))

        self.people = []

        self.entities = {
            "hospitals": self.hospitals,
            "people": self.people,
        }

    def _load_sprite(self, path: str, size: tuple[int, int]) -> pygame.Surface:
        sprite = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(sprite, size)

    def _load_sprites(self) -> dict[str, pygame.Surface]:
        ambulance_base = self._load_sprite("images/ambulance.png", (16, 16))
        ambulance_lights = ambulance_base.copy()
        ambulance_lights.fill((255, 80, 80, 235), special_flags=pygame.BLEND_RGBA_MULT)
        ambulance_mask = pygame.mask.from_surface(ambulance_base)
        ambulance_outline = ambulance_mask.to_surface(setcolor=(245, 246, 230, 190), unsetcolor=(0, 0, 0, 0))
        hospital_base = self._load_sprite("images/hospital.png", (34, 34))
        return {
            "hospital": hospital_base,
            "person": self._load_sprite("images/person.png", (16, 16)),
            "ambulance": ambulance_base,
            "ambulance_lights": ambulance_lights,
            "ambulance_outline": ambulance_outline,
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

    def _geo_to_screen(self, longitude: float, latitude: float, map):
        return hlp.transform_coordinates(
            latitude,
            longitude,
            map.min_latitude,
            map.max_latitude,
            map.min_longitude,
            map.max_longitude,
        )

    def _draw_ambulance(self, screen, ambulance, map, now_seconds: float):
        x, y = self._geo_to_screen(ambulance.long, ambulance.lat, map)
        rotation = -ambulance.direction

        outline = pygame.transform.rotozoom(self.sprites["ambulance_outline"], rotation, 1.18)
        outline_rect = outline.get_rect(center=(x, y))
        screen.blit(outline, outline_rect)

        base = pygame.transform.rotozoom(self.sprites["ambulance"], rotation, 1.0)
        base_rect = base.get_rect(center=(x, y))
        screen.blit(base, base_rect)

        pulse = 0.5 + 0.5 * (1.0 + pygame.math.Vector2(1, 0).rotate(now_seconds * 360.0).x)
        light_alpha = int(80 + 170 * pulse)
        lights = pygame.transform.rotozoom(self.sprites["ambulance_lights"], rotation, 1.0)
        lights.set_alpha(light_alpha)
        lights_rect = lights.get_rect(center=(x, y))
        screen.blit(lights, lights_rect)

        beacon_radius = int(6 + 6 * pulse)
        beacon_surface = pygame.Surface((beacon_radius * 2 + 4, beacon_radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(
            beacon_surface,
            (255, 70, 60, int(70 + 90 * pulse)),
            (beacon_radius + 2, beacon_radius + 2),
            beacon_radius,
            0,
        )
        pygame.draw.circle(
            beacon_surface,
            (255, 210, 160, int(120 + 90 * pulse)),
            (beacon_radius + 2, beacon_radius + 2),
            max(2, beacon_radius // 3),
            0,
        )
        screen.blit(beacon_surface, (x - beacon_radius - 2, y - beacon_radius - 2))

        dispatch_age = now_seconds - ambulance.dispatch_started_at
        if 0.0 <= dispatch_age <= 1.2:
            ripple_progress = dispatch_age / 1.2
            radius = int(8 + 34 * ripple_progress)
            alpha = int(120 * (1.0 - ripple_progress))
            ripple_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(
                ripple_surface,
                (255, 212, 120, alpha),
                (radius + 2, radius + 2),
                radius,
                2,
            )
            screen.blit(ripple_surface, (x - radius - 2, y - radius - 2))

    def _draw_hospital(self, screen, hospital, map, now_seconds: float):
        x, y = self._geo_to_screen(hospital.longitude, hospital.latitude, map)
        pulse = 0.5 + 0.5 * (1.0 + pygame.math.Vector2(1, 0).rotate(now_seconds * 140.0).x)

        glow_radius = int(20 + 8 * pulse)
        glow_surface = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (210, 255, 220, int(80 + 80 * pulse)),
            (glow_radius + 2, glow_radius + 2),
            glow_radius,
            0,
        )
        pygame.draw.circle(
            glow_surface,
            (60, 170, 90, int(70 + 70 * pulse)),
            (glow_radius + 2, glow_radius + 2),
            max(6, glow_radius // 2),
            0,
        )
        screen.blit(glow_surface, (x - glow_radius - 2, y - glow_radius - 2))

        station = self.sprites["hospital"]
        station_rect = station.get_rect(center=(x, y))
        screen.blit(station, station_rect)

    def draw(self, screen, map, now_seconds: float = 0.0):
        for hospital in self.entities["hospitals"]:
            self._draw_hospital(screen, hospital, map, now_seconds)

        for person in self.entities["people"]:
            self._draw_sprite_at_geo(
                screen,
                self.sprites["person"],
                person.longitude,
                person.latitude,
                map,
            )

        for hospital in self.entities["hospitals"]:
            for ambulance in list(hospital.ambulances.values()):
                self._draw_ambulance(screen, ambulance, map, now_seconds)
    
    def update(self, now_seconds: float, dt_seconds: float):
        for hospital in self.entities["hospitals"]:
            hospital.update(self.people, now_seconds)
            for ambulance in list(hospital.ambulances.values()):
                ambulance.update(dt_seconds)

    def remove_person(self, person):
        if person in self.people:
            self.people.remove(person)
class Hospital:
    def __init__(self, name, longitude, latitude, pf, entities):
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.pathfinding = pf
        self.map = pf.map
        self.parent = entities
        
        self.pursuit = False
        self.scan_interval_seconds = 1.0
        self.last_scan_seconds = -self.scan_interval_seconds
        self.closest_cell = self.pathfinding.get_closest_cell(self.longitude, self.latitude)

        self.ambulances = {}
        self.ambulance_limit = 2
    
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

        if len(self.ambulances) < self.ambulance_limit:
            self.dispatch_ambulance(closest, path)
        

    def dispatch_ambulance(self, person, path):
        ambulance = Ambulance(self, person, path)
        self.ambulances[id(ambulance)] = ambulance
        person.rescuer = ambulance
             
        

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
    

class Ambulance():

    def __init__(self, station, target, path):
        self.speed_km_per_second = 0.25
        self.parent = station
        self.target = target
        self.path = path
        self.lat = station.latitude
        self.long = station.longitude
        self.dispatch_started_at = pygame.time.get_ticks() / 1000.0

        self.trajectory = self.get_complete_path()
        self.loaded = False
        self.arrival_threshold_km = 0.006

        if self.trajectory:
             self.update_direction()
        else:
            self.trajectory_target = None
            self.direction = 0
            self.lat_vector = 0
            self.long_vector = 0
            

    def update(self, dt_seconds: float):
        if not self.trajectory or not self.trajectory_target:

            if not self.loaded:
                self.transport_target()
            elif self.loaded and hlp.get_distance(self.lat, self.long, self.parent.latitude, self.parent.longitude) < 0.1:
                del self.parent.ambulances[id(self)]

            return

        if self.trajectory and self.trajectory_target:
            self.move_towards_target(dt_seconds)

    def move_towards_target(self, dt_seconds: float):
            target_lat = self.trajectory_target[0]
            target_long = self.trajectory_target[1]
            distance_to_target = hlp.get_distance(self.lat, self.long, target_lat, target_long)

            if distance_to_target <= self.arrival_threshold_km:
                self.lat = target_lat
                self.long = target_long
                self.update_direction()
                return

            max_step_km = self.speed_km_per_second * max(0.001, dt_seconds)
            if max_step_km >= distance_to_target:
                self.lat = target_lat
                self.long = target_long
                self.update_direction()
                return

            ratio = max_step_km / distance_to_target
            self.lat += (target_lat - self.lat) * ratio
            self.long += (target_long - self.long) * ratio
            self.direction = hlp.get_direction(self.lat, self.long, target_lat, target_long)

    def update_direction(self):
        if self.trajectory:
            self.trajectory.pop(0)

        if not self.trajectory:
            self.trajectory_target = None
            return
        self.trajectory_target = self.trajectory[0]
        self.direction = hlp.get_direction(self.lat, self.long, self.trajectory_target[0], self.trajectory_target[1])
        self.lat_vector = hlp.get_normalized_lonlan(self.direction)[1]
        self.long_vector = hlp.get_normalized_lonlan(self.direction)[0]
    
    def get_complete_path(self):

        complete_path = []
        for i, node in enumerate(self.path):
            current_node = node
            if i < len(self.path) - 1:

                next_node = self.path[i + 1]
                edge_data = self.parent.map.G.get_edge_data(current_node, next_node)
                
                geom = edge_data[0].get("geometry")
                
                if geom:
                    for point in geom.coords:
                        complete_path.append((point[1], point[0]))
                else:
                    current = self.parent.map.G.nodes[current_node]
                    next = self.parent.map.G.nodes[next_node]      
                    complete_path.append((current["y"], current["x"]))
                    complete_path.append((next["y"], next["x"]))
        cleaned_path = []
        for waypoint in complete_path:
            if cleaned_path and hlp.get_distance(cleaned_path[-1][0], cleaned_path[-1][1], waypoint[0], waypoint[1]) < 0.0004:
                continue
            cleaned_path.append(waypoint)
        return cleaned_path

    def transport_target(self):
        self.loaded = True
        self.parent.parent.remove_person(self.target)
        self.path = self.parent.pathfinding.run_astar(self.target.closest_cell, self.parent.closest_cell)
        self.target = self.parent
        self.trajectory = self.get_complete_path()
        self.update_direction()
        
    