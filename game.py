import sys

import pygame

from loading_screen import show_retro_loading_screen
from map import Map
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from pathfinding import Pathfinding
import entities


class Game:
	def __init__(self) -> None:
		pygame.init()
		pygame.display.set_caption("ARIA")
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.clock = pygame.time.Clock()
		self.last_mouse_click_pos: tuple[int, int] | None = None
		self.last_mouse_button: int | None = None
		self.loaded_map = show_retro_loading_screen(
			self.screen,
			self.clock,
			lambda: Map(self.screen),
		)
		self.pathfinding = Pathfinding(self.loaded_map)
		self.running = True
		self.entities = entities.Entities(self.loaded_map)

	def _handle_keydown(self, key: int) -> None:
		if key == pygame.K_ESCAPE:
			self.running = False

	def _handle_mouse_click(self, event: pygame.event.Event) -> None:
		self.last_mouse_click_pos = event.pos
		self.last_mouse_button = event.button

	def _handle_events(self) -> None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			elif event.type == pygame.KEYDOWN:
				self._handle_keydown(event.key)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				self._handle_mouse_click(event)

	def run(self) -> None:
		while self.running:
			self._handle_events()

			self.screen.fill((20, 24, 28))
			self.loaded_map.draw()
			self.entities.draw(self.screen, self.loaded_map)
			pygame.display.flip()
			self.clock.tick(60)

		pygame.quit()
		sys.exit(0)
