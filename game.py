import sys
import math

import pygame

from loading_screen import show_retro_loading_screen
from map import Map
from settings import SCREEN_HEIGHT, SCREEN_WIDTH, THEME_BG, GENERATION_DURATION
from pathfinding import Pathfinding
from generations import Generations
from title_screen import show_title_screen
from end_game_screen import show_end_game_screen
import entities


class Game:
	def __init__(self) -> None:
		pygame.init()
		pygame.display.set_caption("ARIA")
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.screen.fill(THEME_BG)
		pygame.display.flip()
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
		self.shift_selector_open = False
		self.shift_options: list[str] = []
		self.shift_selected_index = 0
		self.shift_feedback_text = ""
		self.shift_feedback_until_ms = 0

		self.pathfinding = Pathfinding(self.loaded_map)
		self.entities = entities.Entities(self.loaded_map, self.pathfinding, self)
		self.generations = Generations(self.entities, self.loaded_map, self)
		self.shift_options = self.generations.get_shiftable_freguesias()

	def _open_population_shift_selector(self) -> None:
		self.shift_options = self.generations.get_shiftable_freguesias()
		if not self.shift_options:
			self.shift_feedback_text = "No freguesia options available"
			self.shift_feedback_until_ms = pygame.time.get_ticks() + 2200
			return
		self.shift_selector_open = True
		self.shift_selected_index = 0

	def _draw_population_shift_selector(self) -> None:
		if not self.shift_selector_open or not self.shift_options:
			return

		panel_w, panel_h = 560, 300
		panel_x = (SCREEN_WIDTH - panel_w) // 2
		panel_y = (SCREEN_HEIGHT - panel_h) // 2

		overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 120))
		self.screen.blit(overlay, (0, 0))

		panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
		panel.fill((12, 9, 4, 235))
		pygame.draw.rect(panel, (175, 118, 28), panel.get_rect(), 2, border_radius=8)
		self.screen.blit(panel, (panel_x, panel_y))

		title = self.ui_font.render("POPULATION SHIFT (+20% TO +30%)", True, (255, 208, 82))
		self.screen.blit(title, (panel_x + 18, panel_y + 14))
		help_text = self.ui_small_font.render("UP/DOWN select | ENTER apply | ESC cancel", True, (150, 120, 60))
		self.screen.blit(help_text, (panel_x + 18, panel_y + 40))

		visible_count = 9
		start = max(0, self.shift_selected_index - visible_count // 2)
		end = min(len(self.shift_options), start + visible_count)
		if end - start < visible_count:
			start = max(0, end - visible_count)

		y = panel_y + 72
		for idx in range(start, end):
			name = self.shift_options[idx]
			selected = idx == self.shift_selected_index
			if selected:
				sel_bg = pygame.Surface((panel_w - 36, 24), pygame.SRCALPHA)
				sel_bg.fill((70, 48, 12, 180))
				self.screen.blit(sel_bg, (panel_x + 18, y - 3))
			color = (255, 208, 82) if selected else (200, 150, 60)
			prefix = "> " if selected else "  "
			label = self.ui_small_font.render(prefix + name, True, color)
			self.screen.blit(label, (panel_x + 22, y))
			y += 25
	

	def _handle_keydown(self, key: int) -> None:
		if self.shift_selector_open:
			if key == pygame.K_ESCAPE:
				self.shift_selector_open = False
			elif key in (pygame.K_UP, pygame.K_w):
				self.shift_selected_index = (self.shift_selected_index - 1) % len(self.shift_options)
			elif key in (pygame.K_DOWN, pygame.K_s):
				self.shift_selected_index = (self.shift_selected_index + 1) % len(self.shift_options)
			elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
				selected = self.shift_options[self.shift_selected_index]
				applied = self.generations.trigger_population_shift(selected)
				if applied:
					self.shift_feedback_text = f"Shift applied: {selected}"
				else:
					self.shift_feedback_text = "Shift failed for selected freguesia"
				self.shift_feedback_until_ms = pygame.time.get_ticks() + 2500
				self.shift_selector_open = False
			return

		if key == pygame.K_ESCAPE:
			self.running = False
		elif key == pygame.K_m:
			self._open_population_shift_selector()
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

	def _draw_generations_hud(self, sim_seconds: float) -> None:
		# Use static amber colors
		hud_bg = (14, 10, 3)
		hud_border = (175, 118, 28)
		hud_text = (255, 208, 82)
		hud_text_dim = (150, 120, 60)
		hud_accent = (255, 180, 50)
		
		panel_x, panel_y = 14, 14
		panel_w, panel_h = 385, 212
		panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
		panel_surface.fill(hud_bg)
		pygame.draw.rect(panel_surface, hud_border, panel_surface.get_rect(), 1, border_radius=5)
		self.screen.blit(panel_surface, (panel_x, panel_y))

		time_left = self.generations.get_time_left_in_generation(sim_seconds)
		time_elapsed = self.generations.get_time_in_generation(sim_seconds)
		time_total = self.generations.generation_duration_seconds
		progress = 0.0 if time_total <= 0 else min(1.0, max(0.0, time_elapsed / time_total))
		people_count = self.generations.get_people_on_map_count()
		ambulances_count = self.generations.get_ambulances_dispatched_count()
		dead_count = len(self.generations.dead_people)

		px = panel_x + 16
		py = panel_y + 13

		# Header
		aria_surf = self.ui_small_font.render("ARIA", True, hud_text_dim)
		gen_surf  = self.ui_title_font.render(f"GEN {self.generations.current_generation:02d}", True, hud_text)
		self.screen.blit(aria_surf, (px, py + 5))
		self.screen.blit(gen_surf,  (px + 46, py))

		# Divider
		div_y = py + 30
		pygame.draw.line(self.screen, hud_border, (panel_x + 12, div_y), (panel_x + panel_w - 12, div_y), 1)

		# Time row
		ty = div_y + 10
		e_lbl = self.ui_small_font.render("ELAPSED",   True, hud_text_dim)
		e_val = self.ui_font.render(f"{time_elapsed:07.1f}s", True, hud_text)
		r_lbl = self.ui_small_font.render("REMAINING", True, hud_text_dim)
		r_val = self.ui_font.render(f"{time_left:07.1f}s",    True, hud_accent)
		self.screen.blit(e_lbl, (px,       ty))
		self.screen.blit(e_val, (px,       ty + 16))
		self.screen.blit(r_lbl, (px + 192, ty))
		self.screen.blit(r_val, (px + 192, ty + 16))

		# Progress bar
		bar_y = ty + 48
		bar_x = panel_x + 12
		bar_w = panel_w - 24
		bar_h = 7
		pygame.draw.rect(self.screen, (22, 16, 5), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
		pygame.draw.rect(self.screen, hud_border,   (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)
		fill_w = int((bar_w - 4) * progress)
		if fill_w > 0:
			pygame.draw.rect(self.screen, hud_accent, (bar_x + 2, bar_y + 2, fill_w, bar_h - 4), border_radius=2)

		# Stats (2x2 grid)
		sy = bar_y + 20
		col = (panel_w - 32) // 2

		def _stat(label, value, x, y, vc=None):
			self.screen.blit(self.ui_small_font.render(label, True, hud_text_dim), (x, y))
			self.screen.blit(self.ui_font.render(value, True, vc or hud_text), (x, y + 16))

		_stat("PEOPLE",     f"{people_count:03d}",       px,        sy)
		_stat("DISPATCHED", f"{ambulances_count:03d}",   px + col,  sy)
		_stat("DEAD",       f"{dead_count:03d}",          px,        sy + 38, (210, 78, 52))
		_stat("SPEED",      f"x{self.game_speed:.1f}",   px + col,  sy + 38)

		controls_hint = self.ui_small_font.render("M: POP SHIFT MENU", True, (150, 120, 60))
		self.screen.blit(controls_hint, (panel_x + 14, panel_y + panel_h - 38))

		if self.generations.population_shift_target:
			shift_label = self.ui_small_font.render(
				f"SHIFT: {self.generations.population_shift_target[:42]}",
				True,
				(255, 180, 50),
			)
			self.screen.blit(shift_label, (panel_x + 14, panel_y + panel_h - 20))

		now_ms = pygame.time.get_ticks()
		if self.shift_feedback_text and now_ms <= self.shift_feedback_until_ms:
			feedback = self.ui_small_font.render(self.shift_feedback_text, True, (255, 208, 82))
			self.screen.blit(feedback, (panel_x + 14, panel_y + panel_h + 8))
 
	def _draw_retro_overlay(self) -> None:
		pass
	
	def _draw_retro_background(self) -> None:
		# Subtle static amber colors
		bg_color = (9, 7, 5)  # Very dark amber background
		grid_color = (22, 16, 5)  # Subtle amber grid
		grid_h_color = (25, 18, 6)  # Subtle amber horizontal grid
		
		self.screen.fill(bg_color)

		center_x = SCREEN_WIDTH // 2
		horizon = int(SCREEN_HEIGHT * 0.18)
		for i in range(-22, 23):
			offset = i * 56 + int(math.sin(pygame.time.get_ticks() / 1000.0 * 0.65 + i * 0.25) * 7)
			pygame.draw.line(
				self.screen,
				grid_color,
				(center_x + offset, SCREEN_HEIGHT),
				(center_x + int(offset * 0.08), horizon),
				1,
			)

		for row in range(7):
			y = int(horizon + (row ** 1.7) * 16)
			if y < SCREEN_HEIGHT:
				pygame.draw.line(self.screen, grid_h_color, (0, y), (SCREEN_WIDTH, y), 1)

		vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
		pygame.draw.rect(vignette, (0, 0, 0, 75), vignette.get_rect(), width=55, border_radius=22)
		self.screen.blit(vignette, (0, 0))

	def run(self) -> None:
		show_title_screen(self.screen, self.clock)
		
		while self.running:
			self._handle_events()
			sim_now_seconds = self.simulation_now_seconds

			if not self.shift_selector_open:
				dt_seconds = max(1.0 / 120.0, self.clock.get_time() / 1000.0)
				self.simulation_now_seconds += dt_seconds * self.game_speed
				sim_now_seconds = self.simulation_now_seconds
				self.generations.update(sim_now_seconds)
				self.entities.update(sim_now_seconds, dt_seconds, self.game_speed)

			self._draw_retro_background()

			self.loaded_map.draw()
			self.entities.draw(self.screen, self.loaded_map, sim_now_seconds)
			self._draw_retro_overlay()
			self._draw_generations_hud(sim_now_seconds)
			self._draw_population_shift_selector()
			pygame.display.flip()
			self.clock.tick(60)

		# Get overall statistics before exiting
		overall_stats = self.generations.get_overall_stats()
		
		# Show end-game stats screen
		show_end_game_screen(self.screen, self.clock, overall_stats)

		pygame.quit()
		sys.exit(0)
