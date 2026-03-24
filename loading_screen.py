import threading
import queue
import pygame


GREEN = (84, 255, 159)
DARK = (9, 16, 12)
BLACK = (0, 0, 0)


def show_retro_loading_screen(screen: pygame.Surface, clock: pygame.time.Clock, load_fn):
    """Display a retro loading screen while load_fn executes in a worker thread."""
    result_queue = queue.Queue(maxsize=1)

    def worker() -> None:
        try:
            result_queue.put(("ok", load_fn()))
        except Exception as exc:  # pragma: no cover
            result_queue.put(("error", exc))

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    width, height = screen.get_size()
    title_font = pygame.font.SysFont("consolas", 44, bold=True)
    text_font = pygame.font.SysFont("consolas", 20, bold=True)
    tiny_font = pygame.font.SysFont("consolas", 14)

    tick = 0
    status_text = "CONNECTING TO STREET GRID"

    while thread.is_alive() or result_queue.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit(0)

        tick += 1
        phase = (tick % 180) / 180.0
        pulse = 90 + int(70 * abs(phase - 0.5) * 2)

        screen.fill(DARK)

        # CRT-style scanlines for a retro monitor feel.
        for y in range(0, height, 4):
            pygame.draw.line(screen, (5, 10, 7), (0, y), (width, y), 1)

        glow = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(glow, (20, 70, 40, 45), (40, 70, width - 80, height - 140), border_radius=12)
        screen.blit(glow, (0, 0))

        title = title_font.render("ARIA MAP LINK", True, GREEN)
        screen.blit(title, ((width - title.get_width()) // 2, 110))

        frame_rect = pygame.Rect(180, 250, width - 360, 28)
        pygame.draw.rect(screen, (20, 40, 30), frame_rect, border_radius=4)
        pygame.draw.rect(screen, GREEN, frame_rect, 2, border_radius=4)

        bars = 24
        active = (tick // 6) % bars
        segment_w = (frame_rect.width - 8) // bars
        for i in range(bars):
            x = frame_rect.x + 4 + i * segment_w
            color = (30, pulse, 95) if i <= active else (10, 25, 18)
            pygame.draw.rect(screen, color, (x, frame_rect.y + 4, segment_w - 2, frame_rect.height - 8))

        if tick % 90 == 0:
            dots = "." * ((tick // 90) % 4)
            status_text = f"CONNECTING TO STREET GRID{dots}"

        status = text_font.render(status_text, True, GREEN)
        hint = tiny_font.render("PRESS ESC TO EXIT", True, (55, 150, 90))
        screen.blit(status, ((width - status.get_width()) // 2, 300))
        screen.blit(hint, ((width - hint.get_width()) // 2, 355))

        pygame.display.flip()
        clock.tick(60)

    state, payload = result_queue.get()
    if state == "error":
        raise payload
    return payload