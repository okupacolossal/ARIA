import time

import pygame
from helpers import Helpers as hlp
import heapq
import random
from settings import GENERATION_DURATION, PERSON_SPAWNING_TIMER, PRIORITIES, FREGUESIA_WEIGHTS


class Entities:
    """Owns game entities and handles update/draw orchestration."""

    def __init__(self, map, pf, game):
        self.map = map
        self.sprites = self._load_sprites()
        self.pathfinding = pf
        self.game = game

        self.hospitals = [Hospital("Hospital Santa Maria", -8.6095796, 41.1600076, pf, self)]

        # Background thread pool for pathfinding and other heavy lifting
        import concurrent.futures
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)

        # People are managed externally now (your custom spawner can append here).
        self.people = []
        self.ambulances = {}
        self.dead_people = []

    def register_ambulance(self, ambulance):
        self.ambulances[id(ambulance)] = ambulance

    def unregister_ambulance(self, ambulance):
        self.ambulances.pop(id(ambulance), None)

    def get_hospital_ambulance_count(self, hospital) -> int:
        return sum(1 for ambulance in self.ambulances.values() if ambulance.parent is hospital)

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
        
        # Animate and draw the path
        if hasattr(ambulance, 'full_trajectory_cache') and len(ambulance.full_trajectory_cache) > 1:
            if ambulance.drawn_path_index < len(ambulance.full_trajectory_cache):
                # Animate 3 waypoints per frame to make it fast but visible
                ambulance.drawn_path_index = min(len(ambulance.full_trajectory_cache), ambulance.drawn_path_index + 3)
            
            points = []
            for i in range(ambulance.drawn_path_index):
                lat, lon, _ = ambulance.full_trajectory_cache[i]
                sx, sy = self._geo_to_screen(lon, lat, map)
                points.append((sx, sy))
                
            if len(points) >= 2:
                pygame.draw.lines(screen, ambulance.path_color, False, points, 3)

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
        for hospital in self.hospitals:
            self._draw_hospital(screen, hospital, map, now_seconds)

        for person in self.people:
            self._draw_sprite_at_geo(
                screen,
                self.sprites["person"],
                person.longitude,
                person.latitude,
                map,
            )

        for ambulance in list(self.ambulances.values()):
            self._draw_ambulance(screen, ambulance, map, now_seconds)
    
    def update(self, now_seconds: float, dt_seconds: float, speed_multiplier: float = 1.0):
        for hospital in self.hospitals:
            hospital.update(self.people, now_seconds)

        for ambulance in list(self.ambulances.values()):
            ambulance.update(dt_seconds, speed_multiplier)

    def remove_person(self, person):
        if person in self.people:
            self.people.remove(person)

    def add_person(self, current_sim_time):
        values = list(PRIORITIES.keys())
        priority = random.choice(values)
        time_to_live = random.randint(PRIORITIES[priority][0], PRIORITIES[priority][1]) * 60 
        freguesia = random.choices(
        list(FREGUESIA_WEIGHTS.keys()),
        weights=list(FREGUESIA_WEIGHTS.values()),
        k=1
        )[0]

        longitude, latitude = self.map.get_random_available_point_in_freguesia(freguesia)

        longitude = max(self.map.min_longitude, min(self.map.max_longitude, longitude))
        latitude = max(self.map.min_latitude, min(self.map.max_latitude, latitude))
        
        person = Person(
            name=f"Person_{len(self.people) + 1}",
            longitude=longitude,
            latitude=latitude,
            time_to_live=time_to_live,
            priority=priority,
            spawn_time=current_sim_time,
            pf=self.pathfinding,
            parent=self,
        )
        self.people.append(person)


        




        
class Hospital:
    """Dispatch center that scans for unassigned people and sends ambulances."""

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

        self.ambulance_limit = 2
    
    def analyze_surroundings(self, people): 
        if self.parent.get_hospital_ambulance_count(self) >= self.ambulance_limit:
            return

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

            heapq.heappush(list_of_people, (person.priority, distance, person))

        closest = heapq.heappop(list_of_people)[2] if list_of_people else None
        if closest is None:
            return

        if closest.closest_cell is None:
            closest.closest_cell = self.pathfinding.get_closest_cell(
                closest.longitude,
                closest.latitude,
            )

        # Mark as pending dispatch to prevent other hospitals/ticks from grabbing them
        closest.rescuer = True  

        def on_path_calculated(future):
            try:
                path = future.result()
                # Check limit again just in case another ambulance spawned while calculating
                if self.parent.get_hospital_ambulance_count(self) < self.ambulance_limit:
                    self.dispatch_ambulance(closest, path)
                else:
                    closest.rescuer = None
            except Exception as e:
                print(f"Error calculating path: {e}")
                closest.rescuer = None

        future = self.parent.thread_pool.submit(
            self.pathfinding.run_astar, self.closest_cell, closest.closest_cell
        )
        
        future.add_done_callback(on_path_calculated)
        

    def dispatch_ambulance(self, person, path):
        ambulance = Ambulance(self, person, path)
        self.parent.register_ambulance(ambulance)
        person.rescuer = ambulance
             
        

    def update(self, people, now_seconds: float):
        if self.pursuit:
            return

        if (now_seconds - self.last_scan_seconds) < self.scan_interval_seconds:
            return

        self.last_scan_seconds = now_seconds
        self.analyze_surroundings(people)
    


class Person:
    """Simple person model with an optional shelf-life timer."""

    def __init__(self, name, longitude, latitude, time_to_live: float = 30.0, spawn_time: float = 0.0, pf=None, parent=None, priority=3):
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.time_to_live = time_to_live
        self.spawn_time = spawn_time
        self.rescuer = None
        self.pf = pf
        self.closest_cell = None
        self.parent = parent
        self.priority = priority

    def is_alive(self, now_seconds: float) -> bool:
        if (now_seconds - self.spawn_time) < self.time_to_live:
            return True
        else:
            self.parent.game.generations.dead_people[self.name] = (self.latitude, self.longitude)
            print('Appended new dead person to list, will remove from map immediately')
            return False
    

class Ambulance():
    """Follows an A* route toward target and then returns to hospital."""


    def __init__(self, station, target, path):
        self.parent = station
        self.target = target
        self.path = path
        self.lat = station.latitude
        self.long = station.longitude
        self.dispatch_started_at = pygame.time.get_ticks() / 1000.0

        self.path_color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

        self.trajectory = self.get_complete_path()
        self.full_trajectory_cache = list(self.trajectory)
        self.drawn_path_index = 0

        self.loaded = False
        self.arrival_threshold_km = 0.006

        if self.trajectory:
             self.update_direction()
        else:
            self.trajectory_target = None
            self.direction = 0
            

    def update(self, dt_seconds: float, speed_multiplier: float = 1.0):
        if not self.trajectory or not self.trajectory_target:

            if not self.loaded:
                self.transport_target()
            elif self.loaded and hlp.get_distance(self.lat, self.long, self.parent.latitude, self.parent.longitude) < 0.1:
                self.parent.parent.unregister_ambulance(self)

            return

        if self.trajectory and self.trajectory_target:
            self.move_towards_target(dt_seconds, speed_multiplier)

    def move_towards_target(self, dt_seconds: float, speed_multiplier: float):
        time_left = max(0.001, dt_seconds) * max(0.0, speed_multiplier)
        
        while time_left > 0.001 and self.trajectory_target is not None:
            target_lat = self.trajectory_target[0]
            target_long = self.trajectory_target[1]
            speed_limit_kph = self.trajectory_target[2]
            distance_to_target = hlp.get_distance(self.lat, self.long, target_lat, target_long)

            speed_km_per_second = self._speed_from_limit(speed_limit_kph)
            # Avoid division by zero
            if speed_km_per_second <= 0:
                speed_km_per_second = 0.001

            if distance_to_target <= self.arrival_threshold_km:
                self.lat = target_lat
                self.long = target_long
                self.update_direction()
                continue

            max_step_km = speed_km_per_second * time_left
            if max_step_km >= distance_to_target:
                time_taken = distance_to_target / speed_km_per_second
                time_left -= time_taken
                self.lat = target_lat
                self.long = target_long
                self.update_direction()
            else:
                ratio = max_step_km / distance_to_target
                self.lat += (target_lat - self.lat) * ratio
                self.long += (target_long - self.long) * ratio
                self.direction = hlp.get_direction(self.lat, self.long, target_lat, target_long)
                time_left = 0

    def update_direction(self):
        # Consume current waypoint and point to the next one.
        if self.trajectory:
            self.trajectory.pop(0)

        if not self.trajectory:
            self.trajectory_target = None
            return
        
        self.trajectory_target = self.trajectory[0]
        self.direction = hlp.get_direction(self.lat, self.long, self.trajectory_target[0], self.trajectory_target[1])

    def _extract_speed_limit_kph(self, edge_attrs) -> float:
        # Parse OSM maxspeed values (supports strings, lists, and mph suffixes).
        raw_speed = edge_attrs.get("maxspeed")
        if raw_speed is None:
            return 50.0

        if isinstance(raw_speed, list):
            candidates = raw_speed
        else:
            candidates = [raw_speed]

        values = []
        for candidate in candidates:
            text = str(candidate).lower().strip()
            if not text:
                continue

            number_chars = []
            for ch in text:
                if ch.isdigit() or ch == ".":
                    number_chars.append(ch)
                elif number_chars:
                    break

            if not number_chars:
                continue

            try:
                value = float("".join(number_chars))
            except ValueError:
                continue

            if "mph" in text:
                value *= 1.60934

            values.append(value)

        if not values:
            return 50.0

        return max(10.0, min(130.0, values[0]))

    def _speed_from_limit(self, speed_limit_kph: float) -> float:
        return speed_limit_kph / 3600.0
    
    def get_complete_path(self):
        # Build (lat, lon, speed_limit_kph) waypoints from graph edges.

        complete_path = []
        for i, node in enumerate(self.path):
            current_node = node
            if i < len(self.path) - 1:

                next_node = self.path[i + 1]
                edge_data = self.parent.map.G.get_edge_data(current_node, next_node)
                if not edge_data:
                    continue
                edge_attrs = edge_data[0] if edge_data and 0 in edge_data else next(iter(edge_data.values()))
                speed_limit_kph = self._extract_speed_limit_kph(edge_attrs)

                geom = edge_attrs.get("geometry")
                
                if geom:
                    for point in geom.coords:
                        complete_path.append((point[1], point[0], speed_limit_kph))
                else:
                    current = self.parent.map.G.nodes[current_node]
                    next = self.parent.map.G.nodes[next_node]      
                    complete_path.append((current["y"], current["x"], speed_limit_kph))
                    complete_path.append((next["y"], next["x"], speed_limit_kph))
        cleaned_path = []
        for waypoint in complete_path:
            if cleaned_path and hlp.get_distance(cleaned_path[-1][0], cleaned_path[-1][1], waypoint[0], waypoint[1]) < 0.0004:
                continue
            cleaned_path.append(waypoint)
        return cleaned_path

    def transport_target(self):
        # Once the person is reached, remove them and route back to station.
        self.loaded = True
        self.parent.parent.remove_person(self.target)
        self.path = self.parent.pathfinding.run_astar(self.target.closest_cell, self.parent.closest_cell)
        self.target = self.parent
        
        # Give it a new arbitrary path color on return, or could keep it
        self.path_color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        
        self.trajectory = self.get_complete_path()
        self.full_trajectory_cache = list(self.trajectory)
        self.drawn_path_index = 0
        
        self.update_direction()
        
    