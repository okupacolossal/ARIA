SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Day/Night cycle - colors transition from amber (day) to blue (night)
# 0.0 = start of day (amber), 0.5 = noon (transition to blue), 1.0 = end of day (blue)

# Amber phosphor palette (day)
AMBER_PALETTE = {
    "bg": (9, 7, 5),           # background
    "bright": (255, 208, 82),  # A1 - bright amber
    "mid": (220, 155, 35),     # A2 - mid amber
    "border": (175, 118, 28),  # A3 - border
    "dim": (132, 92, 30),      # A4 - dim
    "very_dark": (48, 32, 5),  # A5 - very dark
    "grid": (28, 20, 7),       # grid lines
    "grid_h": (32, 23, 8),     # grid horizontal
    "hud_bg": (10, 8, 4, 215), # HUD background with alpha
    "hud_text": (238, 182, 58),
    "hud_text_dim": (132, 92, 30),
    "hud_accent": (255, 222, 108),
}

# Blue phosphor palette (night)
BLUE_PALETTE = {
    "bg": (5, 7, 12),          # background
    "bright": (100, 200, 255), # bright cyan/blue
    "mid": (60, 150, 220),     # mid blue
    "border": (40, 120, 200),  # border
    "dim": (30, 90, 160),      # dim
    "very_dark": (10, 20, 40), # very dark
    "grid": (20, 40, 60),      # grid lines
    "grid_h": (25, 50, 70),    # grid horizontal
    "hud_bg": (5, 15, 30, 215),       # HUD background with alpha
    "hud_text": (100, 200, 255),
    "hud_text_dim": (60, 120, 180),
    "hud_accent": (150, 220, 255),
}

THEME_BG = AMBER_PALETTE["bg"]

PERSON_SPAWNING_TIMER = 144
GENERATION_DURATION = 3600   # 1 simulated hour per generation (compressed from 24h)
PEOPLE_PER_GENERATION = 50   # ~1200/day equivalent; 72 s between spawns

PRIORITIES = {
    1: [8, 15],
    2: [15, 24],
    3: [24, 35]
}

FREGUESIA_WEIGHTS = {
    "Cedofeita, Santo Ildefonso, Sé, Miragaia, São Nicolau e Vitória": 0.093,
    "Paranhos": 0.071,
    "Campanhã": 0.054,
    "Ramalde": 0.061,
    "Bonfim": 0.051,
    "Aldoar, Foz do Douro e Nevogilde": 0.055,
    "Lordelo do Ouro e Massarelos": 0.046,
    "Matosinhos": 0.058,
    "Senhora da Hora": 0.045,
    "São Mamede de Infesta": 0.048,
    "Pedrouços": 0.021,
    "Rio Tinto": 0.087,
    "Fânzeres e São Pedro da Cova": 0.058,
    "Gondomar (São Cosme), Valbom e Jovim": 0.045,
    "Santa Marinha": 0.051,
    "Canidelo": 0.044,
    "São Pedro da Afurada": 0.011,
    "Oliveira do Douro": 0.038,
    "nan": 0.013,  # remainder
}