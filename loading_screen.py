import threading
import queue
import math
import pygame


AMBER        = (220, 155, 35)
AMBER_BRIGHT = (255, 208, 82)
AMBER_DIM    = (130, 88, 18)
AMBER_DARK   = (55, 36, 6)
BG           = (9, 7, 5)


def show_retro_loading_screen(screen: pygame.Surface, clock: pygame.time.Clock, load_fn):
    """Display a retro loading screen while load_fn executes in a worker thread."""
    result_queue = queue.Queue(maxsize=1)

    def worker() -> None:
        try:
            result_queue.put(("ok", load_fn()))
        except Exception as exc:
            result_queue.put(("error", exc))

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    width, height = screen.get_size()
    title_font = pygame.font.SysFont("consolas", 52, bold=True)
    sub_font   = pygame.font.SysFont("consolas", 16, bold=True)
    text_font  = pygame.font.SysFont("consolas", 18, bold=True)
    tiny_font  = pygame.font.SysFont("consolas", 13)

    tick = 0
    cx = width // 2

    while thread.is_alive() or result_queue.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit(0)

        tick += 1
        t = tick / 60.0

        screen.fill(BG)

        # Subtle scanlines
        for y in range(0, height, 3):
            pygame.draw.line(screen, (15, 11, 3), (0, y), (width, y), 1)

        # Pulsing title
        pulse = 0.72 + 0.28 * math.sin(t * 2.2)
        c = tuple(int(ch * pulse) for ch in AMBER_BRIGHT)
        title = title_font.render("ARIA", True, c)
        screen.blit(title, (cx - title.get_width() // 2, 148))

        subtitle = sub_font.render("EMERGENCY DISPATCH SYSTEM", True, AMBER_DIM)
        screen.blit(subtitle, (cx - subtitle.get_width() // 2, 214))

        # Thin divider
        pygame.draw.line(screen, AMBER_DARK, (cx - 110, 240), (cx + 110, 240), 1)

        # Progress bar
        bar_w = 300
        bar_h = 6
        bar_x = cx - bar_w // 2
        bar_y = 290
        fill_frac = (tick % 150) / 150.0
        fill_w = int(bar_w * fill_frac)

        pygame.draw.rect(screen, (22, 16, 5), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        pygame.draw.rect(screen, AMBER_DARK,  (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)
        if fill_w > 0:
            pygame.draw.rect(screen, AMBER, (bar_x, bar_y, fill_w, bar_h), border_radius=3)

        # Status text
        dots = "." * ((tick // 40) % 4)
        status = text_font.render(f"CONNECTING TO STREET GRID{dots}", True, AMBER_DIM)
        hint   = tiny_font.render("ESC TO EXIT", True, (65, 44, 8))
        screen.blit(status, (cx - status.get_width() // 2, 316))
        screen.blit(hint,   (cx - hint.get_width()   // 2, 380))

        pygame.display.flip()
        clock.tick(60)

    state, payload = result_queue.get()
    if state == "error":
        raise payload
    return payload
