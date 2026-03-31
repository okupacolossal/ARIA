from settings import GENERATION_DURATION, PERSON_SPAWNING_TIMER, PRIORITIES
import random
import time

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
        self.person_timer_seconds = GENERATION_DURATION / 600.0  # 600 people per day
        self.last_spawned_time = 0.0
        self.game = game
        self.game_speed = game.game_speed
        self.dead_people = {}

        self.current_generation = 0
        self.generation_started_at = None
        self.ambulances_dispatched = 0

    def start_new_generation(self, now_seconds: float):
        # Advance generation index and let custom spawn hook run.
        self.current_generation += 1
        self.generation_started_at = now_seconds
        self.last_spawned_time = now_seconds

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
        
        
