# ARIA - Adaptive Response Intelligence Agent

ARIA is a simulation project for emergency response planning in Porto, Portugal. It models people spawning across freguesias, dispatches ambulances from multiple stations through a real street graph, tracks outcomes by generation, and helps evaluate better station placement.

## Project Goals

- Simulate emergency demand over time using weighted district populations.
- Dispatch ambulances through realistic road topology.
- Compare generation performance (deaths, dispatches, timing).
- Experiment with station strategies and population shifts.
- Provide an end-of-run summary with a suggested best station location.

## Core Functionality

- Real-map simulation using Porto graph and freguesia data.
- Dynamic people spawning with urgency levels (priority and time-to-live).
- Ambulance dispatch and return flow.
- Multi-generation lifecycle with statistics memory.
- Test-station repositioning based on demand hotspots.
- Manual population-shift event with in-game selector.
- End-game analytics screen.

## Controls

- `ESC`: End simulation and open final stats screen.
- `UP` / `RIGHT`: Increase simulation speed.
- `DOWN` / `LEFT`: Decrease simulation speed.
- `M`: Open population shift selector.
- In selector:
- `UP` / `DOWN` (or `W` / `S`): Navigate freguesias.
- `ENTER`: Apply population shift.
- `ESC`: Cancel selector.

## End-of-Run Output

When the simulation ends, ARIA shows:

- Total generations processed.
- Total deaths.
- Total ambulances dispatched.
- Average deaths per generation.
- Mortality rate.
- Recommended best station location based on demand/death hotspot aggregation.

## Project Structure

- `main.py`: Entry point.
- `game.py`: Main loop, rendering, HUD, controls, population shift UI.
- `entities.py`: People, ambulances, hospitals, drawing and behavior logic.
- `generations.py`: Generation timing, spawning cadence, historical stats, shift weighting.
- `map.py`: Graph/freguesia loading, coordinate conversion, map drawing.
- `pathfinding.py`: Routing/pathfinding logic.
- `helpers.py`: Shared utility functions.
- `title_screen.py`: Intro/title experience.
- `loading_screen.py`: Retro loading interface.
- `end_game_screen.py`: Final summary and recommendation screen.
- `settings.py`: Simulation constants, palette, base freguesia weights.
- `porto_map.graphml`: Street graph data.
- `porto_freguesias.gpkg`: Freguesia geospatial boundaries.

## Data and Simulation Model

- Time is simulated and can be accelerated.
- Each generation has configurable duration and spawn pacing.
- Priority determines person urgency and survival window.
- Spawn distribution is weighted by freguesia.
- Runtime population shifts alter weights in real time.
- Stats are accumulated to inform adaptive station recommendations.

## Skills Developed in This Project

- Geospatial simulation design (graph + district-level weights).
- Real-time game loop architecture with Pygame.
- Event-driven UI and keyboard interaction design.
- Pathfinding integration for emergency routing.
- Systems balancing (spawn rates, modifiers, speed scaling).
- Data robustness and fallback handling.
- Iterative visual design for thematic consistency.
- Analytics-driven decision support (generation memory and station recommendation).

## How to Run

## Requirements

- Python 3.10+
- Pygame
- OSMnx
- GeoPandas
- NetworkX

Install dependencies (example):

```bash
pip install pygame osmnx geopandas networkx
```

Run:

```bash
python main.py
```

## Notes

- The simulation uses local map files in this repository.
- Population shifts are temporary runtime strategy interventions.
- End-of-run recommendations are heuristic and based on observed demand patterns during the session.
