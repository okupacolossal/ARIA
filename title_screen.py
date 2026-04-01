import math
import random
import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT


# Amber phosphor palette
A1  = (255, 208,  82)   # bright amber
A2  = (220, 155,  35)   # mid amber
A3  = (175, 118,  28)   # border
A4  = (132,  92,  30)   # dim
A5  = ( 48,  32,   5)   # very dark
BG  = (  9,   7,   5)   # background


def show_title_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    width, height = screen.get_size()

    DIV_X    = width  // 2
    RADAR_CX = DIV_X + (width - DIV_X) // 2   # 960
    RADAR_CY = height // 2                      # 360
    RADAR_R  = 190
    LX       = 72
    MID      = RADAR_R + 2                     # used inside radar surfaces

    # ── Fonts ────────────────────────────────────────────────────
    logo_font  = pygame.font.SysFont("consolas",   82, bold=True)
    acro_font  = pygame.font.SysFont("couriernew", 12, bold=True)
    head_font  = pygame.font.SysFont("couriernew", 13, bold=True)
    body_font  = pygame.font.SysFont("couriernew", 13)
    tag_font   = pygame.font.SysFont("couriernew", 11, bold=True)
    enter_font = pygame.font.SysFont("consolas",   15, bold=True)

    # ── Static pre-renders ───────────────────────────────────────
    logo_main = logo_font.render("ARIA", True, A1)
    logo_glow = logo_font.render("ARIA", True, (40, 26, 5))

    ACRO_LINES = [("A", "DAPTIVE"), ("R", "ESPONSE"), ("I", "NTELLIGENCE"), ("A", "GENT")]
    acro_surfs = [(acro_font.render(b, True, A2), acro_font.render(r, True, A4))
                  for b, r in ACRO_LINES]

    DESC = [
        "A simulation engine for optimal emergency",
        "resource placement in urban environments.",
        "",
        "Each generation evaluates a candidate station",
        "using real OSM street topology and district-",
        "level population density data from Porto, PT.",
        "",
        "Best-performing coordinates are carried forward",
        "via a moving average convergence algorithm.",
    ]
    desc_surfs = [(body_font.render(ln, True, A4) if ln else None) for ln in DESC]

    TAGS  = ["OSM GRAPH", "A* PATHFINDING", "GEN. OPTIMIZATION", "REAL-TIME SIM"]
    RADAR_TITLE = head_font.render("DISPATCH NETWORK OVERVIEW", True, A4)
    PORTO_LBL   = head_font.render("PORTO, PT", True, A4)

    # Concentric ring surfaces (static)
    ring_surfs = []
    for r_f in [0.25, 0.5, 0.75, 1.0]:
        r = int(RADAR_R * r_f)
        alpha = 110 if r_f == 1.0 else 48
        rs = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(rs, (*A5, alpha), (r+2, r+2), r, 1)
        ring_surfs.append((r, rs))

    # Crosshair surface (static)
    ch_s = pygame.Surface((RADAR_R*2+4, RADAR_R*2+4), pygame.SRCALPHA)
    pygame.draw.line(ch_s, (*A5, 65), (MID, 2),   (MID, RADAR_R*2+2), 1)
    pygame.draw.line(ch_s, (*A5, 65), (2,   MID), (RADAR_R*2+2, MID), 1)

    # Scanline overlay (static)
    scanlines = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, 3):
        pygame.draw.line(scanlines, (0, 0, 0, 26), (0, y), (width, y), 1)

    # ── Radar blips – seeded for reproducibility ─────────────────
    rng = random.Random(7)
    blips = []
    for _ in range(26):
        dist  = rng.uniform(30, RADAR_R - 16)
        angle = rng.uniform(0, math.tau)
        blips.append({
            'ox': math.cos(angle) * dist,
            'oy': math.sin(angle) * dist,
            'base_angle': angle % math.tau,
            'glow': 0.0,
            'phase': rng.uniform(0, math.tau),
        })

    sweep_angle = 0.0
    SWEEP_SPEED = math.tau / (60 * 5)   # one full rotation every 5 s

    tick = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit(0)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return

        tick += 1
        t = tick / 60.0
        prev_sweep  = sweep_angle
        sweep_angle = (sweep_angle + SWEEP_SPEED) % math.tau

        # Blip glow update
        for blip in blips:
            ba  = blip['base_angle']
            lit = (prev_sweep <= ba <= sweep_angle) if prev_sweep <= sweep_angle \
                  else (ba >= prev_sweep or ba <= sweep_angle)
            blip['glow'] = 1.0 if lit else max(0.0, blip['glow'] - 0.009)

        # ── Background ───────────────────────────────────────────
        screen.fill(BG)

        cx_g = width // 2
        hor  = int(height * 0.18)
        for i in range(-22, 23):
            off = i * 56 + int(math.sin(t * 0.65 + i * 0.25) * 7)
            pygame.draw.line(screen, (28, 20, 7),
                             (cx_g + off, height),
                             (cx_g + int(off * 0.08), hor), 1)
        for row in range(7):
            gy = int(hor + (row ** 1.7) * 16)
            if gy < height:
                pygame.draw.line(screen, (32, 23, 8), (0, gy), (width, gy), 1)

        screen.blit(scanlines, (0, 0))
        pygame.draw.line(screen, A5, (DIV_X, 36), (DIV_X, height - 36), 1)

        # ── LEFT PANEL ───────────────────────────────────────────
        pulse      = 0.88 + 0.12 * math.sin(t * 1.6)
        pulse_alp  = int(180 + 75 * math.sin(t * 1.6))

        # ARIA glow (offset renders)
        for dx, dy in [(-4,-4),(-4,4),(4,-4),(4,4),(0,-5),(0,5),(-5,0),(5,0)]:
            screen.blit(logo_glow, (LX + dx, 70 + dy))
        logo_main.set_alpha(pulse_alp)
        screen.blit(logo_main, (LX, 70))

        # Acronym
        ay = 70 + logo_main.get_height() + 8
        for bs, rs in acro_surfs:
            screen.blit(bs, (LX + 4, ay))
            screen.blit(rs, (LX + 4 + bs.get_width(), ay))
            ay += 15

        # Separator
        sep_y = ay + 14
        pygame.draw.line(screen, A3, (LX, sep_y), (DIV_X - 40, sep_y), 1)

        # Description
        dy = sep_y + 16
        for surf in desc_surfs:
            if surf is None:
                dy += 6
            else:
                screen.blit(surf, (LX, dy))
                dy += 17

        # Feature tags
        dy += 10
        tx = LX
        for tag in TAGS:
            ts = tag_font.render(tag, True, A3)
            tw = ts.get_width() + 14
            pygame.draw.rect(screen, (18, 13, 4), (tx, dy, tw, 20), border_radius=3)
            pygame.draw.rect(screen, A5,           (tx, dy, tw, 20), 1, border_radius=3)
            screen.blit(ts, (tx + 7, dy + 5))
            tx += tw + 7
            if tx + 80 > DIV_X - 20:
                tx  = LX
                dy += 26

        # PRESS ENTER (blinking)
        ent_y = height - 66
        pygame.draw.line(screen, A5, (LX, ent_y - 14), (DIV_X - 40, ent_y - 14), 1)
        if (tick // 35) % 2 == 0:
            ent_s = enter_font.render("[ PRESS ENTER TO BEGIN ]", True, A2)
            screen.blit(ent_s, (LX, ent_y))

        # ── RIGHT PANEL – RADAR ──────────────────────────────────

        # Outer ambient glow
        ga    = int(28 + 14 * math.sin(t * 1.1))
        glow_s = pygame.Surface((RADAR_R*2+80, RADAR_R*2+80), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (*A5, ga),
                           (RADAR_R+40, RADAR_R+40), RADAR_R + 38)
        screen.blit(glow_s, (RADAR_CX - RADAR_R - 40, RADAR_CY - RADAR_R - 40))

        # Radar background fill
        pygame.draw.circle(screen, (11, 8, 3), (RADAR_CX, RADAR_CY), RADAR_R)

        # Concentric rings
        for r, rs in ring_surfs:
            screen.blit(rs, (RADAR_CX - r - 2, RADAR_CY - r - 2))

        # Crosshairs
        screen.blit(ch_s, (RADAR_CX - RADAR_R - 2, RADAR_CY - RADAR_R - 2))

        # Sweep trail
        trail_s = pygame.Surface((RADAR_R*2+4, RADAR_R*2+4), pygame.SRCALPHA)
        TRAIL_ARC   = math.pi * 0.55
        TRAIL_STEPS = 60
        for i in range(TRAIL_STEPS):
            frac = i / TRAIL_STEPS
            ang  = sweep_angle - TRAIL_ARC * (1.0 - frac)
            alp  = int(125 * frac * frac)
            ex   = MID + math.cos(ang) * RADAR_R
            ey   = MID + math.sin(ang) * RADAR_R
            pygame.draw.line(trail_s, (*A2, alp), (MID, MID), (int(ex), int(ey)), 2)
        screen.blit(trail_s, (RADAR_CX - RADAR_R - 2, RADAR_CY - RADAR_R - 2))

        # Sweep leading edge
        se_x = int(RADAR_CX + math.cos(sweep_angle) * RADAR_R)
        se_y = int(RADAR_CY + math.sin(sweep_angle) * RADAR_R)
        pygame.draw.line(screen, A1, (RADAR_CX, RADAR_CY), (se_x, se_y), 2)

        # Blips
        for blip in blips:
            bx = int(RADAR_CX + blip['ox'] + math.sin(t * 0.6 + blip['phase']) * 1.5)
            by = int(RADAR_CY + blip['oy'] + math.cos(t * 0.8 + blip['phase']) * 1.5)
            g  = blip['glow']
            if g > 0.04:
                gr   = int(2 + 12 * g)
                bs_s = pygame.Surface((gr*2+4, gr*2+4), pygame.SRCALPHA)
                pygame.draw.circle(bs_s, (*A2, int(140 * g)), (gr+2, gr+2), gr)
                screen.blit(bs_s, (bx - gr - 2, by - gr - 2))
            dc = tuple(int(c * max(0.15, g)) for c in A1) if g > 0.04 else A5
            pygame.draw.circle(screen, dc, (bx, by), 2)

        # Border ring on top (masks any overflow)
        pygame.draw.circle(screen, A3, (RADAR_CX, RADAR_CY), RADAR_R, 1)

        # Center crosshair dot
        pygame.draw.circle(screen, A3, (RADAR_CX, RADAR_CY), 4)
        pygame.draw.circle(screen, A1, (RADAR_CX, RADAR_CY), 2)

        # Radar labels
        screen.blit(RADAR_TITLE,
                    (RADAR_CX - RADAR_TITLE.get_width() // 2, RADAR_CY - RADAR_R - 28))
        screen.blit(PORTO_LBL,
                    (RADAR_CX - PORTO_LBL.get_width()  // 2, RADAR_CY + RADAR_R + 12))

        # Vignette
        vig = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(vig, (0, 0, 0, 85), vig.get_rect(), width=70, border_radius=20)
        screen.blit(vig, (0, 0))

        pygame.display.flip()
        clock.tick(60)
