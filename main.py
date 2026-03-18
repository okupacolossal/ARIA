import pygame
import sys
import random
import map
import constants
import entities
import game as game_module
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
    pathfinder = None

    state = "config"
    init_steps_done = 0
    state_start_ticks = pygame.time.get_ticks()

    running = True
    while running:

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if state == "config":
                start_boot = loading_screen.handle_config_event(event)
                if start_boot:
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
                    pathfinder = pathfinding.Pathfinder()
                    init_steps_done = 0
                    state = "loading"
                    state_start_ticks = pygame.time.get_ticks()

            if state == "playing" and event.type == pygame.MOUSEBUTTONDOWN:
                if grid is not None and grid.initialized:
                    mouse_pos = pygame.mouse.get_pos()
                    pathfinder.cell_click(game.stations[0].closest_passable, mouse_pos, grid)

        # --- Update ---
        if state == "loading" and grid is not None:
            frame_budget_start = pygame.time.get_ticks()
            while pygame.time.get_ticks() - frame_budget_start < INIT_TIME_BUDGET_MS:
                try:
                    init_steps_done += next(grid_init)
                except StopIteration:
                    break
            if grid.initialized:
                spawn_cell = get_random_station_cell(grid)
                game.add_station(station=entities.Station(spawn_cell, grid, pathfinder))
                state = "playing"
                state_start_ticks = pygame.time.get_ticks()

        # --- Draw ---
        screen.fill(constants.BLACK)
        elapsed_ms = pygame.time.get_ticks() - state_start_ticks

        if state == "config":
            loading_screen.draw_configuration(screen=screen, elapsed_ms=elapsed_ms)
        elif state == "loading":
            loading_screen.draw(
                screen=screen,
                progress_steps=init_steps_done,
                elapsed_ms=elapsed_ms,
            )
        elif state == "playing" and game is not None and grid is not None:
            game.update()
            game.draw(grid, screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
