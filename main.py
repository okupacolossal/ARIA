import sys
import map
import pygame
from loading_screen import show_retro_loading_screen


def main() -> None:
	pygame.init()
	pygame.display.set_caption("ARIA")
	screen = pygame.display.set_mode((960, 540))
	clock = pygame.time.Clock()
	loaded_map = show_retro_loading_screen(screen, clock, lambda: map.Map())

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				running = False

		screen.fill((20, 24, 28))
		pygame.display.flip()
		clock.tick(60)

	pygame.quit()
	sys.exit(0)


if __name__ == "__main__":
	main()
 