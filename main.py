import sys
import map
import pygame

loaded_map = map.Map()


def main() -> None:
	pygame.init()
	pygame.display.set_caption("ARIA")
	screen = pygame.display.set_mode((960, 540))
	clock = pygame.time.Clock()

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
 