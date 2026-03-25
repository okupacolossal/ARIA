import sys

import pygame

from loading_screen import show_retro_loading_screen
from map import Map
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from pathfinding import Pathfinding
from generations import Generations
import entities


HUD_BG = (7, 14, 10, 220)
HUD_BORDER = (70, 220, 130)
HUD_TEXT = (145, 255, 190)
HUD_TEXT_DIM = (92, 180, 128)
HUD_ACCENT = (250, 197, 94)


class Game:
	def __init__(self) -> None:
		pygame.init()
		pygame.display.set_caption("ARIA")
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.clock = pygame.time.Clock()
		self.ui_title_font = pygame.font.SysFont("couriernew", 22, bold=True)
		self.ui_font = pygame.font.SysFont("couriernew", 17, bold=True)
		self.ui_small_font = pygame.font.SysFont("couriernew", 14)
		self.last_mouse_click_pos: tuple[int, int] | None = None
		self.last_mouse_button: int | None = None
		self.loaded_map = show_retro_loading_screen(
			self.screen,
			self.clock,
			lambda: Map(self.screen),
		)
		self.running = True

		self.pathfinding = Pathfinding(self.loaded_map)
		self.entities = entities.Entities(self.loaded_map, self.pathfinding)
		self.generations = Generations(self.entities, self.loaded_map)
	def _handle_keydown(self, key: int) -> None:
		if key == pygame.K_ESCAPE:
			self.running = False

	def _handle_events(self) -> None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			elif event.type == pygame.KEYDOWN:
				self._handle_keydown(event.key)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				self._handle_mouse_click(event)

	def _draw_generations_hud(self, now_seconds: float) -> None:
		panel_x, panel_y = 14, 14
		panel_w, panel_h = 410, 180
		panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
		panel_surface.fill(HUD_BG)
		pygame.draw.rect(panel_surface, HUD_BORDER, panel_surface.get_rect(), 2, border_radius=6)

		for y in range(0, panel_h, 4):
			pygame.draw.line(panel_surface, (12, 28, 18, 120), (0, y), (panel_w, y), 1)

		self.screen.blit(panel_surface, (panel_x, panel_y))

		time_left = self.generations.get_time_left_in_generation(now_seconds)
		time_elapsed = self.generations.get_time_in_generation(now_seconds)
		time_total = self.generations.generation_duration_seconds
		progress = 0.0 if time_total <= 0 else min(1.0, max(0.0, time_elapsed / time_total))
		people_count = self.generations.get_people_on_map_count()
		ambulances_count = self.generations.get_ambulances_dispatched_count()

		headline = self.ui_title_font.render(
			f"GENERATION {self.generations.current_generation:02d}",
			True,
			HUD_TEXT,
		)
		self.screen.blit(headline, (panel_x + 14, panel_y + 12))

		line_1 = self.ui_font.render(f"TIME PASSED: {time_elapsed:05.1f}s / {time_total:04.0f}s", True, HUD_TEXT)
		line_2 = self.ui_font.render(f"TIME LEFT:   {time_left:05.1f}s", True, HUD_ACCENT)
		line_3 = self.ui_font.render(f"PEOPLE ON MAP: {people_count:03d}", True, HUD_TEXT)
		line_4 = self.ui_font.render(f"AMBULANCES DISPATCHED: {ambulances_count:03d}", True, HUD_TEXT)
		line_5 = self.ui_small_font.render("placeholder metric for dispatch system", True, HUD_TEXT_DIM)

		self.screen.blit(line_1, (panel_x + 14, panel_y + 52))
		self.screen.blit(line_2, (panel_x + 14, panel_y + 76))
		self.screen.blit(line_3, (panel_x + 14, panel_y + 108))
		self.screen.blit(line_4, (panel_x + 14, panel_y + 132))
		self.screen.blit(line_5, (panel_x + 14, panel_y + 156))

		bar_x = panel_x + 265
		bar_y = panel_y + 74
		bar_w = 142
		bar_h = 13
		pygame.draw.rect(self.screen, (20, 40, 26), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
		pygame.draw.rect(self.screen, HUD_BORDER, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)
		fill_w = int((bar_w - 4) * progress)
		pygame.draw.rect(self.screen, HUD_ACCENT, (bar_x + 2, bar_y + 2, fill_w, bar_h - 4), border_radius=2)

	def _draw_retro_overlay(self) -> None:
		overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
		for y in range(0, SCREEN_HEIGHT, 3):
			pygame.draw.line(overlay, (8, 28, 14, 48), (0, y), (SCREEN_WIDTH, y), 1)
		self.screen.blit(overlay, (0, 0))

	def run(self) -> None:
		while self.running:
			self._handle_events()
			now_seconds = pygame.time.get_ticks() / 1000.0
			self.generations.update(now_seconds)

			self.screen.fill((7, 12, 9))
			self.loaded_map.draw()
			self.entities.update()
			self.entities.draw(self.screen, self.loaded_map)
			self._draw_retro_overlay()
			self._draw_generations_hud(now_seconds)
			pygame.display.flip()
			self.clock.tick(60)

		pygame.quit()
		sys.exit(0)
