from entities import Person

DEFAULT_GENERATION_DURATION_SECONDS = 30.0
DEFAULT_PERSON_TIMER_SECONDS = 30.0
DEFAULT_PEOPLE_PER_GENERATION = 25
DEFAULT_SPAWN_EDGE_MARGIN_RATIO = 0.05


class Generations:
    def __init__(
        self,
        entities,
        map,
        generation_duration_seconds: float = DEFAULT_GENERATION_DURATION_SECONDS,
        person_timer_seconds: float = DEFAULT_PERSON_TIMER_SECONDS,
        people_per_generation: int = DEFAULT_PEOPLE_PER_GENERATION,
        spawn_edge_margin_ratio: float = DEFAULT_SPAWN_EDGE_MARGIN_RATIO,
    ):
        self.entities = entities
        self.map = map
        self.generation_duration_seconds = generation_duration_seconds
        self.person_timer_seconds = person_timer_seconds
        self.people_per_generation = people_per_generation
        self.spawn_edge_margin_ratio = spawn_edge_margin_ratio

        self.current_generation = 0
        self.generation_started_at = None
        self.ambulances_dispatched = 0

    def _create_generation_people(self, now_seconds: float):
        self.entities.people.clear()

        for i in range(self.people_per_generation):
            person_name = f"Person {self.current_generation}-{i + 1}"
            person = Person.create_random(
                person_name,
                self.map,
                edge_margin_ratio=self.spawn_edge_margin_ratio,
                timer_seconds=self.person_timer_seconds,
                spawn_time=now_seconds,
                pf=self.entities.pathfinding

            )
            self.entities.people.append(person)

    def start_new_generation(self, now_seconds: float):
        self.current_generation += 1
        self.generation_started_at = now_seconds
        self._create_generation_people(now_seconds)

    def update(self, now_seconds: float):
        if self.generation_started_at is None:
            self.start_new_generation(now_seconds)
            return

        if (now_seconds - self.generation_started_at) >= self.generation_duration_seconds:
            self.start_new_generation(now_seconds)
            return

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
