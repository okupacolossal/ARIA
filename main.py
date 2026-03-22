import random
import sys

import pygame

import constants
import entities
import game as game_module
import map
import pathfinding
from ui.loading_screen import RetroLoadingScreen

FPS = 60
TITLE = "ARIA"
INIT_TIME_BUDGET_MS = 14
INIT_CHUNK_SIZE = 4096
GRID_SETTINGS = {
    "width": 128,
    "height": 128,
    "grid_pixel_width": 600,
    "grid_pixel_height": 600,
}

STATE_CONFIG = "config"
STATE_LOADING = "loading"
STATE_PLAYING = "playing"


def get_grid_init_total_steps(width, height):
    cell_steps = width * height
    road_steps = ((width - 1) * height) + (width * (height - 1))
    return cell_steps + road_steps


def get_random_station_cell(grid):
    passable_cells = [
        cell
        for column in grid.cells
        for cell in column
        if cell is not None and cell.passable
    ]
    if passable_cells:
        return random.choice(passable_cells)

    all_cells = [cell for column in grid.cells for cell in column if cell is not None]
    return random.choice(all_cells)


def setup_loading_state(selected_settings, loading_screen):
    game = game_module.Game()
    grid = map.Grid(
        selected_settings["width"],
        selected_settings["height"],
        selected_settings["grid_pixel_width"],
        selected_settings["grid_pixel_height"],
        constants.SCREEN_WIDTH,
        constants.SCREEN_HEIGHT,
    )
    grid_init = grid.initialize(chunk_size=INIT_CHUNK_SIZE)

    loading_screen.set_loading_profile(
        grid_settings=selected_settings,
        total_init_steps=get_grid_init_total_steps(grid.width, grid.height),
    )

    game.pathfinder = pathfinding.Pathfinder()
    game.grid = grid
    return game, grid, grid_init


def handle_config_event(event, selected_settings, loading_screen):
    if not loading_screen.handle_config_event(event):
        return None

    game, grid, grid_init = setup_loading_state(selected_settings, loading_screen)
    return {
        "state": STATE_LOADING,
        "game": game,
        "grid": grid,
        "grid_init": grid_init,
        "init_steps_done": 0,
    }


def handle_playing_event(event, game, grid):
    if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
        return

    if grid is None or not grid.initialized:
        return

    if game is None or not game.stations or game.pathfinder is None:
        return

    game.pathfinder.test_path_from_station_click(
        station=game.stations[0],
        mouse_pos=pygame.mouse.get_pos(),
        grid=grid,
    )


def update_loading_state(game, grid, grid_init, init_steps_done):
    if grid is None:
        return {
            "state": STATE_LOADING,
            "game": game,
            "grid": grid,
            "grid_init": grid_init,
            "init_steps_done": init_steps_done,
        }

    frame_budget_start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - frame_budget_start < INIT_TIME_BUDGET_MS:
        try:
            init_steps_done += next(grid_init)
        except StopIteration:
            break

    if grid.initialized and game is not None:
        spawn_cell = get_random_station_cell(grid)
        game.add_station(station=entities.Station(spawn_cell, grid, game.pathfinder, game))
        return {
            "state": STATE_PLAYING,
            "game": game,
            "grid": grid,
            "grid_init": grid_init,
            "init_steps_done": init_steps_done,
        }

    return {
        "state": STATE_LOADING,
        "game": game,
        "grid": grid,
        "grid_init": grid_init,
        "init_steps_done": init_steps_done,
    }


def draw_current_state(screen, state, loading_screen, game, grid, init_steps_done, elapsed_ms):
    if state == STATE_CONFIG:
        loading_screen.draw_configuration(screen=screen, elapsed_ms=elapsed_ms)
        return

    if state == STATE_LOADING:
        loading_screen.draw(
            screen=screen,
            progress_steps=init_steps_done,
            elapsed_ms=elapsed_ms,
        )
        return

    if state == STATE_PLAYING and game is not None and grid is not None:
        game.update()
        game.draw(grid, screen)


def main():
    pygame.init()
    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    selected_settings = GRID_SETTINGS.copy()
    loading_screen = RetroLoadingScreen(
        title=TITLE,
        grid_settings=selected_settings,
        total_init_steps=1,
    )

    game = None
    grid = None
    grid_init = None

    state = STATE_CONFIG
    init_steps_done = 0
    state_start_ticks = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                continue

            if state == STATE_CONFIG:
                transition = handle_config_event(event, selected_settings, loading_screen)
                if transition is not None:
                    state = transition["state"]
                    game = transition["game"]
                    grid = transition["grid"]
                    grid_init = transition["grid_init"]
                    init_steps_done = transition["init_steps_done"]
                    state_start_ticks = pygame.time.get_ticks()
            elif state == STATE_PLAYING:
                handle_playing_event(event, game, grid)

        if state == STATE_LOADING:
            transition = update_loading_state(game, grid, grid_init, init_steps_done)
            previous_state = state
            state = transition["state"]
            game = transition["game"]
            grid = transition["grid"]
            grid_init = transition["grid_init"]
            init_steps_done = transition["init_steps_done"]

            if previous_state != state:
                state_start_ticks = pygame.time.get_ticks()

        screen.fill(constants.BLACK)
        elapsed_ms = pygame.time.get_ticks() - state_start_ticks
        draw_current_state(screen, state, loading_screen, game, grid, init_steps_done, elapsed_ms)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
