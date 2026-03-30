DEFAULT_GENERATION_DURATION_SECONDS = 86400.0
DEFAULT_PERSON_TIMER_SECONDS = 30.0


class Generations:
    """Minimal generation/timer manager.

    Spawning is intentionally disabled so you can implement your own system.
    The only built-in runtime behavior is generation timing and optional cleanup
    of expired people using Person.is_alive.
    """

    def __init__(
        self,
        entities,
        map,
        generation_duration_seconds: float = DEFAULT_GENERATION_DURATION_SECONDS,
        person_timer_seconds: float = DEFAULT_PERSON_TIMER_SECONDS,
    ):
        self.entities = entities
        self.map = map
        self.generation_duration_seconds = generation_duration_seconds
        self.person_timer_seconds = person_timer_seconds

        self.current_generation = 0
        self.generation_started_at = None
        self.ambulances_dispatched = 0

    def _create_generation_people(self, now_seconds: float):
        # Intentionally left empty: plug your custom spawn logic here.
        return

    def start_new_generation(self, now_seconds: float):
        # Advance generation index and let custom spawn hook run.
        self.current_generation += 1
        self.generation_started_at = now_seconds
        self._create_generation_people(now_seconds)

    def update(self, now_seconds: float):
        # Bootstrap first generation on first frame.
        if self.generation_started_at is None:
            self.start_new_generation(now_seconds)
            return

        # Rotate generation when the configured duration elapses.
        if (now_seconds - self.generation_started_at) >= self.generation_duration_seconds:
            self.start_new_generation(now_seconds)
            return

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
