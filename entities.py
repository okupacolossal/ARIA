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
        self.station_name_font = pygame.font.SysFont("couriernew", 14, bold=True)

        self.hospitals = [
            Hospital("Hospital Santa Maria", -8.6095796, 41.1600076, pf, self),
            Hospital("Hospital de São João", -8.611, 41.153, pf, self),
            Hospital("Hospital de Santo António", -8.630, 41.149, pf, self),
            Hospital("Delegação Regional do Norte", -8.630, 41.140, pf, self),]

        # Background thread pool for pathfinding and other heavy lifting
        import concurrent.futures
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)

        # People are managed externally now (your custom spawner can append here).
        self.people = []
        self.ambulances = {}
        self.dead_people = []
        self.test_station = None

    def register_ambulance(self, ambulance):
        self.ambulances[id(ambulance)] = ambulance

    def unregister_ambulance(self, ambulance):
        self.ambulances.pop(id(ambulance), None)

    def upsert_test_station(self, longitude: float, latitude: float, generation_number: int):
        station_name = f"Test Station #{generation_number}"
        if self.test_station is None:
            self.test_station = Hospital(
                station_name,
                longitude,
                latitude,
                self.pathfinding,
                self,
                is_test_station=True,
            )
            self.hospitals.append(self.test_station)
            return

        self.test_station.name = station_name
        self.test_station.longitude = longitude
        self.test_station.latitude = latitude
        self.test_station.closest_cell = self.pathfinding.get_closest_cell(longitude, latitude)

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

        # Draw the cached screen-space path trail (skip at high speeds — invisible anyway)
        if self.game.game_speed <= 480 and hasattr(ambulance, 'screen_path_cache'):
            pts = ambulance.screen_path_cache[:ambulance.drawn_path_index]
            if len(pts) >= 2:
                pygame.draw.lines(screen, ambulance.path_color, False, pts, 3)

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
        pulse_slow = 0.5 + 0.5 * (1.0 + pygame.math.Vector2(1, 0).rotate(now_seconds * 80.0).x)
        mouse_x, mouse_y = pygame.mouse.get_pos()

        glow_radius = int(20 + 8 * pulse)
        glow_surface = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4), pygame.SRCALPHA)
        palette = hospital.palette

        label_surface = self.station_name_font.render(hospital.name, True, palette["label"])
        label_rect = label_surface.get_rect(center=(x, y - 26))
        shadow_surface = self.station_name_font.render(hospital.name, True, palette["shadow"])
        shadow_rect = shadow_surface.get_rect(center=(x + 1, y - 25))

        pygame.draw.circle(
            glow_surface,
            (palette["outer"][0], palette["outer"][1], palette["outer"][2], int(70 + 70 * pulse)),
            (glow_radius + 2, glow_radius + 2),
            glow_radius,
            0,
        )
        pygame.draw.circle(
            glow_surface,
            (palette["inner"][0], palette["inner"][1], palette["inner"][2], int(65 + 65 * pulse)),
            (glow_radius + 2, glow_radius + 2),
            max(6, glow_radius // 2),
            0,
        )
        screen.blit(glow_surface, (x - glow_radius - 2, y - glow_radius - 2))

        station = self.sprites["hospital"]
        station_rect = station.get_rect(center=(x, y))
        screen.blit(station, station_rect)

        if hospital.is_test_station:
            # Make the unique station read as a strategic target point.
            halo_radius = int(28 + 14 * pulse)
            halo_surface = pygame.Surface((halo_radius * 2 + 4, halo_radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(
                halo_surface,
                (226, 242, 255, 130),
                (halo_radius + 2, halo_radius + 2),
                halo_radius,
                3,
            )
            pygame.draw.circle(
                halo_surface,
                (176, 214, 248, 110),
                (halo_radius + 2, halo_radius + 2),
                max(8, halo_radius // 2),
                2,
            )
            scan_radius = int(8 + pulse_slow * (halo_radius - 6))
            pygame.draw.circle(
                halo_surface,
                (210, 235, 255, 90),
                (halo_radius + 2, halo_radius + 2),
                scan_radius,
                1,
            )
            screen.blit(halo_surface, (x - halo_radius - 2, y - halo_radius - 2))

            # Bright center marker to remain visible above roads and boundaries.
            pygame.draw.circle(screen, (242, 250, 255), (x, y), 5)
            pygame.draw.circle(screen, (150, 196, 235), (x, y), 2)

            # Always-visible station banner for fast identification.
            tag_text = self.station_name_font.render(hospital.name.upper(), True, (226, 240, 255))
            tag_shadow = self.station_name_font.render(hospital.name.upper(), True, (30, 44, 60))
            tag_rect = tag_text.get_rect(center=(x, y - 40))
            tag_bg = pygame.Surface((tag_rect.width + 16, tag_rect.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(tag_bg, (18, 28, 40, 210), tag_bg.get_rect(), border_radius=5)
            pygame.draw.rect(tag_bg, (142, 182, 224, 230), tag_bg.get_rect(), 1, border_radius=5)
            screen.blit(tag_bg, (tag_rect.left - 8, tag_rect.top - 4))
            screen.blit(tag_shadow, tag_rect.move(1, 1))
            screen.blit(tag_text, tag_rect)

        hover_radius = max(station_rect.width, station_rect.height) // 2 + 6
        is_station_hovered = (mouse_x - x) ** 2 + (mouse_y - y) ** 2 <= hover_radius ** 2
        is_label_hovered = label_rect.inflate(10, 6).collidepoint(mouse_x, mouse_y)

        if is_station_hovered or is_label_hovered:
            label_bg = pygame.Surface((label_rect.width + 10, label_rect.height + 6), pygame.SRCALPHA)
            pygame.draw.rect(
                label_bg,
                (18, 24, 22, 190),
                label_bg.get_rect(),
                border_radius=4,
            )
            screen.blit(label_bg, (label_rect.left - 5, label_rect.top - 3))
            screen.blit(shadow_surface, shadow_rect)
            screen.blit(label_surface, label_rect)

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

    def __init__(self, name, longitude, latitude, pf, entities, is_test_station: bool = False):
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.pathfinding = pf
        self.map = pf.map
        self.parent = entities
        self.is_test_station = is_test_station
        self.palette = self._random_palette()
        
        self.pursuit = False
        self.scan_interval_seconds = 1.0
        self.last_scan_seconds = -self.scan_interval_seconds
        self.closest_cell = self.pathfinding.get_closest_cell(self.longitude, self.latitude)

        self.ambulance_limit = 1

    def _random_palette(self):
        if self.is_test_station:
            return {
                "outer": (190, 220, 248),
                "inner": (95, 132, 170),
                "label": (218, 236, 255),
                "shadow": (40, 58, 74),
            }

        base = random.randint(110, 210)
        outer = (
            max(80, min(235, base + random.randint(8, 24))),
            max(90, min(245, base + random.randint(10, 28))),
            max(80, min(235, base + random.randint(2, 20))),
        )
        inner = (
            max(50, outer[0] - random.randint(28, 46)),
            max(60, outer[1] - random.randint(34, 52)),
            max(50, outer[2] - random.randint(28, 46)),
        )
        label = (
            min(250, outer[0] + 16),
            min(250, outer[1] + 14),
            min(250, outer[2] + 16),
        )
        shadow = (
            max(20, inner[0] - 28),
            max(24, inner[1] - 28),
            max(20, inner[2] - 28),
        )
        return {
            "outer": outer,
            "inner": inner,
            "label": label,
            "shadow": shadow,
        }
    
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

            # Add a numeric tiebreaker so heap never compares Person objects.
            heapq.heappush(list_of_people, (person.priority, distance, id(person), person))

        closest = heapq.heappop(list_of_people)[3] if list_of_people else None
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
        self.screen_path_cache = self._precompute_screen_path()

        self.loaded = False
        self._computing_return_path = False
        self.arrival_threshold_km = 0.006

        if self.trajectory:
             self.update_direction()
        else:
            self.trajectory_target = None
            self.direction = 0
            

    def _precompute_screen_path(self):
        m = self.parent.map
        return [
            hlp.transform_coordinates(lat, lon, m.min_latitude, m.max_latitude, m.min_longitude, m.max_longitude)
            for lat, lon, _ in self.full_trajectory_cache
        ]

    def update(self, dt_seconds: float, speed_multiplier: float = 1.0):
        advance = max(3, int(speed_multiplier / 15))
        self.drawn_path_index = min(len(self.full_trajectory_cache), self.drawn_path_index + advance)

        if not self.trajectory or not self.trajectory_target:

            if not self.loaded:
                self.transport_target()
            elif self.loaded and not self._computing_return_path and hlp.get_distance(self.lat, self.long, self.parent.latitude, self.parent.longitude) < 0.1:
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
        # Once the person is reached, remove them and route back to station asynchronously.
        self.loaded = True
        self._computing_return_path = True
        self.parent.parent.remove_person(self.target)
        pickup_cell = self.target.closest_cell
        self.target = self.parent
        self.trajectory = []
        self.trajectory_target = None
        self.path_color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

        def on_return_path(future):
            try:
                self.path = future.result()
                self.trajectory = self.get_complete_path()
                self.full_trajectory_cache = list(self.trajectory)
                self.drawn_path_index = 0
                self.screen_path_cache = self._precompute_screen_path()
                if self.trajectory:
                    self.update_direction()
            except Exception as e:
                print(f"Error calculating return path: {e}")
            finally:
                self._computing_return_path = False

        self.parent.parent.thread_pool.submit(
            self.parent.pathfinding.run_astar, pickup_cell, self.parent.closest_cell
        ).add_done_callback(on_return_path)
        
    