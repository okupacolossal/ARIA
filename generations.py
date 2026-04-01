from settings import GENERATION_DURATION, PERSON_SPAWNING_TIMER, PRIORITIES, PEOPLE_PER_GENERATION
import random
import time
from helpers import Helpers as hlp

class Generations:
    """Minimal generation/timer manager.

    Spawning is intentionally disabled so you can implement your own system.
    The only built-in runtime behavior is generation timing and optional cleanup
    of expired people using Person.is_alive.
    """

    def __init__(self, entities, map, game):
        self.entities = entities
        self.map = map
        self.generation_duration_seconds = GENERATION_DURATION
        self.person_timer_seconds = GENERATION_DURATION / PEOPLE_PER_GENERATION
        self.last_spawned_time = 0.0
        self.game = game
        self.game_speed = game.game_speed
        self.dead_people = {}

        self.current_generation = 0
        self.generation_started_at = None
        self.ambulances_dispatched = 0

        self.ghost_station = None

        self.past_generations_stats = {}

    def _reset_dead_counter(self):
        self.dead_people = {}
        # Keep auxiliary entity-level tracking in sync if used elsewhere.
        if hasattr(self.entities, "dead_people"):
            self.entities.dead_people = []

    def _predict_best_station_location(self):
        
        last_avg_locations = [stats["average_death_location"] for stats in list(self.past_generations_stats.values())[-10:]]
        
        estimate_x = last_avg_locations[-1][0]
        estimate_y = last_avg_locations[-1][1]

        for loc in last_avg_locations:
            alpha = 0.1
            estimate_x = alpha * loc[0] + (1 - alpha) * estimate_x if self.ghost_station else loc[0]
            estimate_y = alpha * loc[1] + (1 - alpha) * estimate_y if self.ghost_station else loc[1]

        return estimate_x, estimate_y

    def _update_test_station(self):
        best_location = self._predict_best_station_location()
        if best_location is None:
            return

        best_lat, best_lon = best_location
        self.entities.upsert_test_station(best_lon, best_lat, self.current_generation)
        

    def start_new_generation(self, now_seconds: float):
        # Advance generation index and let custom spawn hook run.

        if self.dead_people:
            self.past_generations_stats[self.current_generation] = {
                "deaths": len(self.dead_people),
                "ambulances": self.ambulances_dispatched,
                "average_death_location": self.average_location(self.dead_people.values())

            }
            self._update_test_station()
        
        self.current_generation += 1
        self.generation_started_at = now_seconds
        self.last_spawned_time = now_seconds
        self._reset_dead_counter()
        self.ambulances_dispatched = 0

        self.clear_people()
        self.clear_ambulances()

        print('generation finished! last generation stats:', self.past_generations_stats.get(self.current_generation - 1, {}))

    def update(self, now_seconds: float):
        # Bootstrap first generation on first frame.

        if self.generation_started_at is None:
            self.start_new_generation(now_seconds)
            return

        # Rotate generation when the configured duration elapses.
        if (now_seconds - self.generation_started_at) >= self.generation_duration_seconds:
            self.start_new_generation(now_seconds)
            return
        
        while (now_seconds - self.last_spawned_time) >= self.person_timer_seconds:
            self.spawn_person(self.last_spawned_time + self.person_timer_seconds)
            self.last_spawned_time += self.person_timer_seconds

        # Keep only people whose shelf-life has not expired.
        self.entities.people[:] = [person for person in self.entities.people if person.is_alive(now_seconds)]

    def get_time_in_generation(self, now_seconds: float) -> float:
        if self.generation_started_at is None:
            return 0.0
        return max(0.0, now_seconds - self.generation_started_at)

    def get_time_left_in_generation(self, now_seconds: float) -> float:
        time_left = self.generation_duration_seconds - self.get_time_in_generation(now_seconds)
        return max(0.0, time_left)

    def get_people_on_map_count(self) -> int:
        return len(self.entities.people)

    def get_ambulances_dispatched_count(self) -> int:
        return self.ambulances_dispatched
    
    def clear_people(self):
        self.entities.people = []

    def clear_ambulances(self):
        self.entities.ambulances = {}
    
    def spawn_person(self, spawn_time):
        self.entities.add_person(spawn_time)
        
    def average_location(self, people):
        avg_lat = sum(lat for lat, _ in people) / len(people)
        avg_lon = sum(lon for _, lon in people) / len(people)
        return avg_lat, avg_lon