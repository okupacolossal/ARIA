import pygame



class RetroHud:
    def __init__(self, game):
        self.panel_bg = (10, 24, 10)
        self.panel_border = (70, 190, 70)
        self.text_main = (125, 255, 125)
        self.text_dim = (82, 170, 82)

        self.title_font = pygame.font.SysFont("consolas", 18, bold=True)
        self.value_font = pygame.font.SysFont("consolas", 16)
        self.game = game

    def draw(self, screen, alive_people, total_people):
        panel = pygame.Rect(18, 16, 290, 88)

        pygame.draw.rect(screen, self.panel_bg, panel)
        pygame.draw.rect(screen, self.panel_border, panel, 2)

        # Thin scanline band for a retro terminal feel.
        pygame.draw.line(
            screen,
            (30, 88, 30),
            (panel.left + 2, panel.top + 28),
            (panel.right - 2, panel.top + 28),
            1,
        )

        title = self.title_font.render("PIP STATUS", True, self.text_main)
        alive = self.value_font.render(f"ALIVE: {alive_people}", True, self.text_main)
        total = self.value_font.render(f"TOTAL: {total_people}", True, self.text_dim)
        current_generation = self.value_font.render(f"GENERATION: {self.game.generations_handler.current_generation}", True, self.text_dim)

        screen.blit(title, (panel.left + 12, panel.top + 8))
        screen.blit(alive, (panel.left + 12, panel.top + 40))
        screen.blit(total, (panel.left + 138, panel.top + 40))
        screen.blit(current_generation, (panel.left + 138, panel.top + 60))
