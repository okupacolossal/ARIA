SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
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