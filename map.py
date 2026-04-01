from networkx import nodes
import osmnx as ox
from settings import *
import pygame
import os
import math
import random
from helpers import Helpers as hlp
import geopandas as gpd

# Subtle static amber colors for streets and boundaries
STREET_COLOR = (80, 60, 20)                    # Subtle amber streets
FREGUESIA_BOUNDARY_COLOR = (110, 85, 30)      # Subtle amber borders
FREGUESIA_LABEL_COLOR = (200, 160, 60)        # Amber labels
FREGUESIA_LABEL_SHADOW_COLOR = (40, 30, 10)   # Dark amber shadow


class Map:
    def __init__(self, screen):
        self.screen = screen
        self.freguesia_font = pygame.font.SysFont("couriernew", 14, bold=True)
        self.nodes = self.get_map()
        self.path = []
    

    def _load_or_create_graph(self):
        if os.path.exists("porto_map.graphml"):
            return ox.load_graphml("porto_map.graphml")

        center = (41.14961, -8.61099)
        graph = ox.graph_from_point(center, dist=7000, network_type="drive")
        ox.save_graphml(graph, "porto_map.graphml")
        return graph

    def _load_freguesias(self):
        if os.path.exists("porto_freguesias.gpkg"):
            return gpd.read_file("porto_freguesias.gpkg")
    
        freguesias = ox.features_from_place(
            "Porto, Porto, Portugal",
            tags={"boundary": "administrative", "admin_level": "8"},
        )
        freguesias = freguesias[
            freguesias.geometry.geom_type.isin(["Polygon", "MultiPolygon"])
        ].copy()
        
        freguesias = freguesias[freguesias["admin_level"] == "8"].copy()
    
        freguesias = freguesias.to_crs(self.gdf.crs)
        freguesias.to_file("porto_freguesias.gpkg", driver="GPKG")
        return freguesias

    def _attach_freguesia_to_nodes(self):
        joined = gpd.sjoin(
            self.gdf,
            self.freguesias,
            how="left",
            predicate="within",
        )
        print(joined.columns.tolist())
        joined = joined[~joined.index.duplicated(keep="first")]
        self.gdf["freguesia"] = joined["name"]

        for node_id in self.G.nodes:
            self.G.nodes[node_id]["freguesia"] = self.gdf.loc[node_id, "freguesia"]
        

    def _compute_geo_bounds(self):
        latitudes = []
        longitudes = []
        for _, data in self.G.nodes(data=True):
            latitudes.append(data["y"])
            longitudes.append(data["x"])

        self.min_latitude = min(latitudes)
        self.max_latitude = max(latitudes)
        self.min_longitude = min(longitudes)
        self.max_longitude = max(longitudes)

    def _geo_to_screen(self, latitude, longitude):
        return hlp.transform_coordinates(
            latitude,
            longitude,
            self.min_latitude,
            self.max_latitude,
            self.min_longitude,
            self.max_longitude,
        )

    def _random_freguesia_color(self, name):
        seeded = random.Random(f"freguesia-border-{name}")
        # Make edges very subtle and dark to be less apparent
        base = seeded.randint(30, 50)
        red = max(20, min(60, base + seeded.randint(-10, 10)))
        green = max(20, min(60, base + seeded.randint(-10, 10)))
        blue = max(20, min(60, base + seeded.randint(-10, 10)))
        return (red, green, blue)

    def _build_freguesia_render_data(self):
        self.freguesia_screen_boundaries = []
        self.freguesia_screen_labels = []

        for _, row in self.freguesias.iterrows():
            name = row.get("name")
            geom = row.geometry
            if not name or geom is None or geom.is_empty:
                continue

            label_point = geom.representative_point()
            label_x, label_y = self._geo_to_screen(label_point.y, label_point.x)
            self.freguesia_screen_labels.append((name, label_x, label_y))

            if geom.geom_type == "Polygon":
                polygons = [geom]
            elif geom.geom_type == "MultiPolygon":
                polygons = list(geom.geoms)
            else:
                continue

            for poly in polygons:
                screen_coords = []
                for x, y in poly.exterior.coords:
                    screen_x, screen_y = self._geo_to_screen(y, x)
                    screen_coords.append((screen_x, screen_y))

                if len(screen_coords) < 2:
                    continue

                self.freguesia_screen_boundaries.append(
                    {
                        "name": name,
                        "coords": screen_coords,
                        "color": self._random_freguesia_color(name),
                        "glitch_seed": random.uniform(0.0, 1000.0),
                    }
                )

        self.freguesia_screen_labels = self._resolve_freguesia_label_overlaps(
            self.freguesia_screen_labels
        )

    def _build_screen_nodes(self):
        screen_nodes = {}
        for node, data in self.G.nodes(data=True):
            screen_nodes[node] = self._geo_to_screen(data["y"], data["x"])
        return screen_nodes

    def _style_edges(self):
        for _, _, data in self.G.edges(data=True):
            edge_length = float(data.get("length", 40.0))
            intensity = max(0.0, min(1.0, edge_length / 220.0))
            
            base_gray = 80 + int(24 * intensity)
            data["line_color"] = (base_gray, base_gray, base_gray)
            data["line_thickness"] = 1

    def _draw_simple_freguesia_boundaries(self):
        for boundary in self.freguesia_screen_boundaries:
            coords = boundary["coords"]
            if len(coords) < 2:
                continue

            base_color = boundary["color"]
            pygame.draw.polygon(self.screen, base_color, coords, width=1)

    def _resolve_freguesia_label_overlaps(self, labels):
        placed = []
        adjusted = []
        padding_x = 6
        padding_y = 4
        offset_step = 14
        max_ring = 3

        for name, screen_x, screen_y in labels:
            text_w, text_h = self.freguesia_font.size(name.upper())

            candidates = [(0, 0)]
            for ring in range(1, max_ring + 1):
                d = ring * offset_step
                candidates.extend([
                    (0, -d),
                    (0, d),
                    (-d, 0),
                    (d, 0),
                    (-d, -d),
                    (d, -d),
                    (-d, d),
                    (d, d),
                ])

            selected_rect = None
            for dx, dy in candidates:
                candidate_x = screen_x + dx
                candidate_y = screen_y + dy
                rect = pygame.Rect(0, 0, text_w + padding_x * 2, text_h + padding_y * 2)
                rect.center = (candidate_x, candidate_y)

                if rect.left < 0 or rect.top < 0 or rect.right > SCREEN_WIDTH or rect.bottom > SCREEN_HEIGHT:
                    continue

                if any(rect.colliderect(existing) for existing in placed):
                    continue

                selected_rect = rect
                break

            if selected_rect is None:
                selected_rect = pygame.Rect(0, 0, text_w + padding_x * 2, text_h + padding_y * 2)
                selected_rect.center = (screen_x, screen_y)

            placed.append(selected_rect)
            adjusted.append((name, selected_rect.centerx, selected_rect.centery))

        return adjusted
    
    def _build_freguesia_node_index(self):
        self.freguesia_nodes = {}
        for node, data in self.G.nodes(data=True):
            f = data.get("freguesia")
            if f:
                self.freguesia_nodes.setdefault(f, []).append(node)

    def get_random_available_point_in_freguesia(self, freguesia):
        nodes = self.freguesia_nodes.get(freguesia, [])
        if not nodes:
            return None
        node_id = random.choice(nodes)
        node_data = self.G.nodes[node_id]
        return node_data["x"], node_data["y"]

    def get_map(self):
        self.G = self._load_or_create_graph()
        self.gdf = ox.graph_to_gdfs(self.G, nodes=True, edges=False)
        self.freguesias = self._load_freguesias()
        print("Map and freguesias loaded, processing...")
    

        sample = next(iter(self.G.nodes(data=True)))[1]
        if "freguesia" not in sample:
            self._attach_freguesia_to_nodes()
            ox.save_graphml(self.G, "porto_map.graphml")
       

        self._compute_geo_bounds()
        self._build_freguesia_render_data()
        self._build_freguesia_node_index()  # <- missing
        self._style_edges()
        

        #print freguesia of each node

        print("Freguesia distribution among nodes:")
        print(set(data.get("freguesia") for _, data in self.G.nodes(data=True)))

        return self._build_screen_nodes()

    def draw(self):
        # Draw streets with static amber color
        for u, v, data in self.G.edges(data=True):
            x1, y1 = self.nodes[u]
            x2, y2 = self.nodes[v]
            pygame.draw.line(self.screen, STREET_COLOR, (x1, y1), (x2, y2), data['line_thickness'])

        # Draw freguesia boundaries with static amber color
        for boundary in self.freguesia_screen_boundaries:
            coords = boundary["coords"]
            if len(coords) < 2:
                continue
            pygame.draw.polygon(self.screen, FREGUESIA_BOUNDARY_COLOR, coords, width=1)

        # Draw freguesia labels with static amber color
        for name, screen_x, screen_y in self.freguesia_screen_labels:
            label_surface = self.freguesia_font.render(name.upper(), True, FREGUESIA_LABEL_COLOR)
            label_rect = label_surface.get_rect(center=(screen_x, screen_y))

            shadow_surface = self.freguesia_font.render(name.upper(), True, FREGUESIA_LABEL_SHADOW_COLOR)
            shadow_rect = shadow_surface.get_rect(center=(screen_x + 1, screen_y + 1))

            self.screen.blit(shadow_surface, shadow_rect)
            self.screen.blit(label_surface, label_rect)
