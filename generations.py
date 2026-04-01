from settings import GENERATION_DURATION, PERSON_SPAWNING_TIMER, PRIORITIES, PEOPLE_PER_GENERATION
import random
import time
from helpers import Helpers as hlp
from settings import FREGUESIA_WEIGHTS

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
        self.base_person_timer_seconds = GENERATION_DURATION / PEOPLE_PER_GENERATION
        self.last_spawned_time = 0.0
        self.game = game
        self.game_speed = game.game_speed
        self.dead_people = {}

        self.current_generation = 0
        self.generation_started_at = None
        self.ambulances_dispatched = 0
        
        # Generation spawn modifier: varies how many people spawn (0.5 = half, 1.5 = 1.5x)
        self.generation_spawn_modifier = 1.0
        self.person_timer_seconds = self.base_person_timer_seconds

        self.ghost_station = None

        self.past_generations_stats = {}
        self.base_spawn_weights = self._build_base_spawn_weights()
        self.current_spawn_weights = dict(self.base_spawn_weights)
        self.population_shift_target = None

    def _build_base_spawn_weights(self):
        # Build from map freguesias first, so the selector always has actionable options.
        available = [
            f for f, nodes in getattr(self.map, "freguesia_nodes", {}).items() if nodes
        ]

        weighted = {}
        for f in available:
            # Use configured weight when present, otherwise assign a small default weight.
            weighted[f] = max(0.0001, float(FREGUESIA_WEIGHTS.get(f, 0.01)))

        # Fallback if map index is unexpectedly empty.
        if not weighted:
            weighted = {k: v for k, v in FREGUESIA_WEIGHTS.items() if v > 0}

        total = sum(weighted.values()) or 1.0
        return {k: v / total for k, v in weighted.items()}

    def get_spawn_weights(self):
        return self.current_spawn_weights

    def get_shiftable_freguesias(self):
        return sorted(self.base_spawn_weights.keys())

    def trigger_population_shift(self, target_freguesia: str, increase_share: float | None = None):
        if target_freguesia not in self.base_spawn_weights:
            return False

        if increase_share is None:
            increase_share = random.uniform(0.20, 0.30)
        increase_share = max(0.20, min(0.30, increase_share))

        # Start from current distribution and bump only the selected freguesia moderately.
        current = dict(self.current_spawn_weights) if self.current_spawn_weights else dict(self.base_spawn_weights)
        target_current = float(current.get(target_freguesia, 0.0))
        target_new = min(0.95, target_current + increase_share)

        others = [f for f in current.keys() if f != target_freguesia]
        others_total = sum(current.get(f, 0.0) for f in others)
        remaining = 1.0 - target_new

        new_weights = {target_freguesia: target_new}

        if others and others_total > 0:
            # Decrease all other freguesias proportionally so total remains 1.0.
            scale = remaining / others_total
            for f in others:
                new_weights[f] = current[f] * scale
        elif others:
            even = remaining / len(others)
            for f in others:
                new_weights[f] = even

        total = sum(new_weights.values()) or 1.0
        self.current_spawn_weights = {k: v / total for k, v in new_weights.items()}
        self.population_shift_target = target_freguesia
        return True

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
                "average_death_location": self.average_location(self.dead_people.values()),
                "spawn_modifier": self.generation_spawn_modifier,
            }
            self._update_test_station()
        
        self.current_generation += 1
        self.generation_started_at = now_seconds
        self.last_spawned_time = now_seconds
        
        # Randomize spawn modifier for this generation (0.6 to 1.5 = less to more people)
        self.generation_spawn_modifier = random.uniform(0.6, 1.5)
        self.person_timer_seconds = self.base_person_timer_seconds / self.generation_spawn_modifier
        
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
    
    def get_overall_stats(self):
        """Get comprehensive overall statistics across all generations."""
        if not self.past_generations_stats:
            return {
                "total_generations": 0,
                "total_deaths": 0,
                "total_ambulances": 0,
                "average_deaths_per_gen": 0,
                "best_station_location": None,
                "worst_coverage_area": None,
            }
        
        stats = self.past_generations_stats
        total_deaths = sum(s["deaths"] for s in stats.values())
        total_ambulances = sum(s["ambulances"] for s in stats.values())
        num_gens = len(stats)
        average_deaths = total_deaths / num_gens if num_gens > 0 else 0
        
        # Calculate best station location based on death hotspot
        all_death_locations = [s["average_death_location"] for s in stats.values() if s["average_death_location"]]
        if all_death_locations:
            # Find the centroid of all deaths
            best_lat = sum(loc[0] for loc in all_death_locations) / len(all_death_locations)
            best_lon = sum(loc[1] for loc in all_death_locations) / len(all_death_locations)
            best_location = (best_lat, best_lon)
        else:
            best_location = None
        
        return {
            "total_generations": num_gens,
            "total_deaths": total_deaths,
            "total_ambulances": total_ambulances,
            "average_deaths_per_gen": average_deaths,
            "best_station_location": best_location,
            "mortality_rate": total_deaths / (total_deaths + total_ambulances * 10) if (total_deaths + total_ambulances * 10) > 0 else 0,
        }