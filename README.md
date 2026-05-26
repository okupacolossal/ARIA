# ðŸš‘ ARIA â€” Adaptive Response Intelligence Agent

A geospatial emergency response simulator for **Porto, Portugal**. Models ambulance dispatch across a real street network, tracks survival outcomes across generations, and recommends optimal station placements based on demand hotspots.

## ðŸŽ¯ What I Built

A Pygame simulation where people spawn across Porto's parishes (*freguesias*) weighted by population, ambulances navigate real OSM street topology to reach them, and each generation's statistics feed an adaptive recommendation engine for station repositioning.

## âœ¨ Features

- **Real map data** â€” Porto street graph via OSMnx + GeoPackage parish boundaries
- **Weighted spawning** â€” emergency demand distributed by parish population
- **Urgency system** â€” priority levels with time-to-live counters
- **Ambulance dispatch** â€” shortest-path routing, dispatch & return flow
- **Multi-generation lifecycle** â€” statistics persist across generations
- **Adaptive recommendations** â€” station placement suggested from death/demand hotspots
- **Population shift events** â€” runtime re-weighting via interactive selector
- **End-game analytics** â€” full summary screen with mortality rate and KPIs

## ðŸ•¹ï¸ Controls

| Key | Action |
|-----|--------|
| `ESC` | End simulation â†’ analytics screen |
| `â†‘` / `â†’` | Increase simulation speed |
| `â†“` / `â†` | Decrease simulation speed |
| `M` | Open population shift selector |
| `â†‘` / `â†“` or `W` / `S` | Navigate parishes in selector |
| `ENTER` | Apply population shift |

## ðŸ› ï¸ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Simulation / Rendering | Pygame |
| Street Graph | OSMnx + NetworkX |
| Geospatial Data | GeoPandas |
| Pathfinding | NetworkX shortest path |

## ðŸ“ Project Structure

```
ARIA/
â”œâ”€â”€ main.py              # Entry point
â”œâ”€â”€ game.py              # Main loop, HUD, rendering, controls
â”œâ”€â”€ entities.py          # People, ambulances, hospitals
â”œâ”€â”€ generations.py       # Generation lifecycle, spawning, stats
â”œâ”€â”€ map.py               # Graph loading, coordinate conversion
â”œâ”€â”€ pathfinding.py       # Routing logic
â”œâ”€â”€ helpers.py           # Shared utilities
â”œâ”€â”€ title_screen.py      # Intro screen
â”œâ”€â”€ loading_screen.py    # Retro loading UI
â”œâ”€â”€ end_game_screen.py   # Final analytics screen
â”œâ”€â”€ settings.py          # Constants, palette, base weights
â”œâ”€â”€ porto_map.graphml    # OSM street graph
â””â”€â”€ porto_freguesias.gpkg # Parish boundaries
```

## ðŸš€ Getting Started

```bash
git clone https://github.com/okupacolossal/ARIA
cd ARIA
pip install pygame osmnx geopandas networkx
python main.py
```

## ðŸ’¡ What I Learned

- Loading and querying real geospatial data (GraphML + GeoPackage)
- Implementing a real-time game loop with variable speed scaling in Pygame
- Integrating graph pathfinding into a live simulation
- Designing weighted probabilistic spawning systems
- Building event-driven UI components (keyboard navigation, modal selectors)
- Aggregating multi-generation statistics into actionable recommendations
- Balancing simulation fidelity with runtime performance
