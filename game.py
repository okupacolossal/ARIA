import sys
import math

import pygame

from loading_screen import show_retro_loading_screen
from map import Map
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from pathfinding import Pathfinding
from generations import Generations
import entities


HUD_BG       = (10, 8, 4, 215)
HUD_BORDER   = (175, 118, 28)
HUD_TEXT     = (238, 182, 58)
HUD_TEXT_DIM = (132, 92, 30)
HUD_ACCENT   = (255, 222, 108)
HUD_DEAD     = (210, 78, 52)


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
		self.game_speed = 360.0
		self.min_game_speed = 1.0
		self.max_game_speed = 14400.0
		self.simulation_now_seconds = 0.0
		self.running = True

		self.pathfinding = Pathfinding(self.loaded_map)
		self.entities = entities.Entities(self.loaded_map, self.pathfinding, self)
		self.generations = Generations(self.entities, self.loaded_map, self)
	def _handle_keydown(self, key: int) -> None:
		if key == pygame.K_ESCAPE:
			self.running = False
		elif key in (pygame.K_UP, pygame.K_RIGHT):
			self.game_speed = min(self.max_game_speed, self.game_speed * 2.0)
		elif key in (pygame.K_DOWN, pygame.K_LEFT):
			self.game_speed = max(self.min_game_speed, self.game_speed / 2.0)

	def _handle_events(self) -> None:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			elif event.type == pygame.KEYDOWN:
				self._handle_keydown(event.key)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				pass

	def _draw_generations_hud(self, now_seconds: float) -> None:
		panel_x, panel_y = 14, 14
		panel_w, panel_h = 385, 212
		panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
		panel_surface.fill(HUD_BG)
		pygame.draw.rect(panel_surface, HUD_BORDER, panel_surface.get_rect(), 1, border_radius=5)
		self.screen.blit(panel_surface, (panel_x, panel_y))

		time_left = self.generations.get_time_left_in_generation(now_seconds)
		time_elapsed = self.generations.get_time_in_generation(now_seconds)
		time_total = self.generations.generation_duration_seconds
		progress = 0.0 if time_total <= 0 else min(1.0, max(0.0, time_elapsed / time_total))
		people_count = self.generations.get_people_on_map_count()
		ambulances_count = self.generations.get_ambulances_dispatched_count()
		dead_count = len(self.generations.dead_people)

		px = panel_x + 16
		py = panel_y + 13

		# Header
		aria_surf = self.ui_small_font.render("ARIA", True, HUD_TEXT_DIM)
		gen_surf  = self.ui_title_font.render(f"GEN {self.generations.current_generation:02d}", True, HUD_TEXT)
		self.screen.blit(aria_surf, (px, py + 5))
		self.screen.blit(gen_surf,  (px + 46, py))

		# Divider
		div_y = py + 30
		pygame.draw.line(self.screen, HUD_BORDER, (panel_x + 12, div_y), (panel_x + panel_w - 12, div_y), 1)

		# Time row
		ty = div_y + 10
		e_lbl = self.ui_small_font.render("ELAPSED",   True, HUD_TEXT_DIM)
		e_val = self.ui_font.render(f"{time_elapsed:07.1f}s", True, HUD_TEXT)
		r_lbl = self.ui_small_font.render("REMAINING", True, HUD_TEXT_DIM)
		r_val = self.ui_font.render(f"{time_left:07.1f}s",    True, HUD_ACCENT)
		self.screen.blit(e_lbl, (px,       ty))
		self.screen.blit(e_val, (px,       ty + 16))
		self.screen.blit(r_lbl, (px + 192, ty))
		self.screen.blit(r_val, (px + 192, ty + 16))

		# Progress bar
		bar_y = ty + 48
		bar_x = panel_x + 12
		bar_w = panel_w - 24
		bar_h = 7
		pygame.draw.rect(self.screen, (22, 16, 5),  (bar_x, bar_y, bar_w, bar_h), border_radius=3)
		pygame.draw.rect(self.screen, HUD_BORDER,   (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)
		fill_w = int((bar_w - 4) * progress)
		if fill_w > 0:
			pygame.draw.rect(self.screen, HUD_ACCENT, (bar_x + 2, bar_y + 2, fill_w, bar_h - 4), border_radius=2)

		# Stats (2x2 grid)
		sy = bar_y + 20
		col = (panel_w - 32) // 2

		def _stat(label, value, x, y, vc=None):
			self.screen.blit(self.ui_small_font.render(label, True, HUD_TEXT_DIM), (x, y))
			self.screen.blit(self.ui_font.render(value, True, vc or HUD_TEXT), (x, y + 16))

		_stat("PEOPLE",     f"{people_count:03d}",       px,        sy)
		_stat("DISPATCHED", f"{ambulances_count:03d}",   px + col,  sy)
		_stat("DEAD",       f"{dead_count:03d}",          px,        sy + 38, HUD_DEAD)
		_stat("SPEED",      f"x{self.game_speed:.1f}",   px + col,  sy + 38)
 
	def _draw_retro_overlay(self) -> None:
		pass

	def _draw_retro_background(self, now_seconds: float) -> None:
		self.screen.fill((9, 7, 5))

		center_x = SCREEN_WIDTH // 2
		horizon = int(SCREEN_HEIGHT * 0.18)
		for i in range(-22, 23):
			offset = i * 56 + int(math.sin(now_seconds * 0.65 + i * 0.25) * 7)
			pygame.draw.line(
				self.screen,
				(28, 20, 7),
				(center_x + offset, SCREEN_HEIGHT),
				(center_x + int(offset * 0.08), horizon),
				1,
			)

		for row in range(7):
			y = int(horizon + (row ** 1.7) * 16)
			if y < SCREEN_HEIGHT:
				pygame.draw.line(self.screen, (32, 23, 8), (0, y), (SCREEN_WIDTH, y), 1)

		vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
		pygame.draw.rect(vignette, (0, 0, 0, 75), vignette.get_rect(), width=55, border_radius=22)
		self.screen.blit(vignette, (0, 0))

	def run(self) -> None:
		while self.running:
			self._handle_events()
			real_now_seconds = pygame.time.get_ticks() / 1000.0
			dt_seconds = max(1.0 / 120.0, self.clock.get_time() / 1000.0)
			self.simulation_now_seconds += dt_seconds * self.game_speed
			sim_now_seconds = self.simulation_now_seconds
			self.generations.update(sim_now_seconds)

			self._draw_retro_background(real_now_seconds)
			self.entities.update(sim_now_seconds, dt_seconds, self.game_speed)

			self.loaded_map.draw()
			self.entities.draw(self.screen, self.loaded_map, real_now_seconds)
			self._draw_retro_overlay()
			self._draw_generations_hud(sim_now_seconds)
			pygame.display.flip()
			self.clock.tick(60)

		pygame.quit()
		sys.exit(0)
