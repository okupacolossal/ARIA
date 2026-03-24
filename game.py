import sys

import pygame

from loading_screen import show_retro_loading_screen
from map import Map
from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class Game:
	def __init__(self) -> None:
		pygame.init()
		pygame.display.set_caption("ARIA")
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.clock = pygame.time.Clock()
		self.loaded_map = show_retro_loading_screen(
			self.screen,
			self.clock,
			lambda: Map(self.screen),
		)

	def run(self) -> None:
		running = True
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
					running = False

			self.screen.fill((20, 24, 28))
			self.loaded_map.draw()
			pygame.display.flip()
			self.clock.tick(60)

		pygame.quit()
		sys.exit(0)
