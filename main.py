import pygame
import sys
import map
import constants
import entities
import game as game_module
import pathfinding

FPS = 60
TITLE = "ARIA"
INIT_STEPS_PER_FRAME = 200

def main():
    pygame.init()
    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    game = game_module.Game()
    grid = map.Grid(128, 128, 600, 600, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, 100)
    grid_init = grid.initialize()
    pathfinder = pathfinding.Pathfinder(grid)

    running = True
    while running:

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                pathfinder.cell_click(mouse_pos)
        # --- Update ---
        if not grid.initialized:
            for _ in range(INIT_STEPS_PER_FRAME):
                try:
                    next(grid_init)
                except StopIteration:
                    break
            if grid.initialized:
                game.add_station(station=entities.Station(grid.cells[13][13]))

        # --- Draw ---
        screen.fill(constants.BLACK)
        game.draw(grid, screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
