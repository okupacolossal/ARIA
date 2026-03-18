import pygame


class Slider:
    def __init__(self, label, min_value, max_value, step, value):
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.value = value
        self.track_rect = pygame.Rect(0, 0, 1, 1)
        self.knob_rect = pygame.Rect(0, 0, 1, 1)

    def set_from_position(self, x_pos):
        ratio = 0.0
        if self.track_rect.width > 0:
            ratio = (x_pos - self.track_rect.left) / self.track_rect.width
        ratio = min(1.0, max(0.0, ratio))

        raw_value = self.min_value + ratio * (self.max_value - self.min_value)
        snapped = round((raw_value - self.min_value) / self.step) * self.step + self.min_value
        self.value = max(self.min_value, min(self.max_value, int(snapped)))

    def get_ratio(self):
        span = self.max_value - self.min_value
        if span <= 0:
            return 0.0
        return (self.value - self.min_value) / span

    def draw(self, screen, x, y, width, body_font, small_font, colors):
        label_color = colors["glow"]
        line_color = colors["line"]
        fill_color = colors["fill"]
        text_dim = colors["dim"]

        label_surface = body_font.render(f"{self.label}: {self.value}", True, label_color)
        screen.blit(label_surface, (x, y))

        self.track_rect = pygame.Rect(x, y + 28, width, 14)
        pygame.draw.rect(screen, line_color, self.track_rect, 2)

        fill_width = int(self.track_rect.width * self.get_ratio())
        if fill_width > 0:
            fill_rect = pygame.Rect(self.track_rect.left + 2, self.track_rect.top + 2, max(1, fill_width - 3), self.track_rect.height - 4)
            pygame.draw.rect(screen, fill_color, fill_rect)

        knob_x = self.track_rect.left + int(self.track_rect.width * self.get_ratio())
        self.knob_rect = pygame.Rect(knob_x - 6, self.track_rect.top - 4, 12, self.track_rect.height + 8)
        pygame.draw.rect(screen, label_color, self.knob_rect)

        min_text = small_font.render(str(self.min_value), True, text_dim)
        max_text = small_font.render(str(self.max_value), True, text_dim)
        screen.blit(min_text, (self.track_rect.left, self.track_rect.bottom + 4))
        screen.blit(max_text, (self.track_rect.right - max_text.get_width(), self.track_rect.bottom + 4))


class RetroLoadingScreen:
    def __init__(self, title, grid_settings, total_init_steps):
        self.title = title
        self.grid_settings = grid_settings
        self.total_init_steps = max(1, total_init_steps)

        self.bg_color = (8, 20, 8)
        self.panel_color = (15, 40, 15)
        self.line_color = (40, 130, 40)
        self.glow_color = (95, 255, 95)
        self.dim_text_color = (60, 180, 60)

        self.header_font = pygame.font.SysFont("consolas", 26, bold=True)
        self.body_font = pygame.font.SysFont("consolas", 17)
        self.small_font = pygame.font.SysFont("consolas", 14)

        self.ascii_art = r"""
                                          ,▄▄▄                              
                                       ▄▓█▀▀▀▀▀█▄                           
               ▄▄▓█`       ,▄▄▓▓▄▄▄▄▄@██▀!√√√√√└▀█▄                         
            .▓█▀██       #█▀▀└:.!╙▀▀██▀:√√√√√√√√√!▀▀█▓▓▄▄                   
           ╓█▀..▀█▓▄▄▄▄▓▀▀:√√√√√√√√√√√√√√√√√√√√√√√√√░░▀▀██▄                 
           ██.√√√!▀▀▀▀▀:√√√√√√√√√√√√√√√√√√√√√√√√√√√√╠░░░░▀█▄                
           █▌√√√√√√√√√√√√√▄▄▄▄▄.√√√√√√√╓▄▄▄.√√√√√√√√╠░░░░░╙█▄               
           ██.√√√√√√√√√▄#█▀╙`╙▀█▓▄▄▄@▓██████▄.√√√√√╠░░░░░░░╙█▓▄             
         ┌████:√√√√√(▄█▀╙       └▀▀▀▀└   └▀▀██,√√╓╢░░░░░░░░░░▀██▄           
         ██:√╙▀▓▄▄▓▓▀▀                      └██▄░░░░░░░░░░░░░░██▄          
         █▌√√╓██▀  ▄▄@╕                       ▀▀█▓▀▀▀▀▀▀███▄░░░░██▄         
         ██▄▓█▀  ╙▀▀▀▀▀                 ,▄               ▀███░░░░██▄        
          ███`                         ▓███,     .        ███░░░░║██        
         ▓█▀     ,▄                     └▀██▄            ▄██▀░░░░░██`       
        ██▀     ███¼        ,              ▀▀        ╓@██▀▀░░░░░░░██        
       ██▀     ▐███       ╓█▀        ▄▄,          .  ▄╙▀█░░░░░░░░╟██        
      ▐█▌       ▀▀└     .▓█└        #███          .  ╙█▓,▀█░░░░░░██▌        
      ██              ▄▓█▀          ███▌          . .▄,▀█▄╙█░░░░███         
     ╟█▌            #██▀            ╙▀▀           .  ▀█▓,█▄╙█░░███          
     ██─            ███                             ▓▄,▀█▄█,█░███`          
     ██             ╙███                         .   ▀█▄╙█Ö█████            
     ██    ,#         ╙╙                         . ╙█▄ ▀ ╙████▀             
     ██  ╒███▄▄                  ▐█▄            .   ╙▀  .@███┘              
     ██▌  ██▄ └╙▀▀#╦▄▄▄▄▄▄▄▄▄▄▄▄#████▄         .         ╙███               
     ▐██   ▀ ▀▓▄,     `└╙└└ .      ███▌        .          ╟██               
      ██▌      ╙▀█▓▄▄▄,   .,▄▄▄▓▓▀▀╙██        .          .███               
      └██▄        └▀▀▀███▀▀▀▀╙"     ▀       ..          ▄███                
       ╙██▄       Ñ▓▓▓▓µ                   ..    ▄▓▓▓▓███▀`                 
        └██▄        `└└                  ..    ▄███▀└└                      
          ▀██▄                          .   ▄▓██▀└                          
            ▀█▓▄                     ..  ▄▓██▀╙                             
              ╙▀█▄,                .╓▄▓██████                               
                 ╙██▓▄         ...   '' ▄██▀                                
                  ╙█████▓▓▄▄▄▄      .▄▄██▀'                                 
                    ▀█████▄▄▄▄▄▄▄▄▓████▀                                    
                       ╙▀▀▀██████▀▀▀╙           
        """.splitlines()

        self.sliders = {
            "grid_size": Slider("GRID SIZE", 32, 192, 8, self.grid_settings["width"]),
        }
        self.dragging_slider = None
        self.start_button_rect = pygame.Rect(0, 0, 1, 1)

    def set_loading_profile(self, grid_settings, total_init_steps):
        self.grid_settings = grid_settings
        self.total_init_steps = max(1, total_init_steps)

    def handle_config_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_button_rect.collidepoint(event.pos):
                return True

            for slider_key, slider in self.sliders.items():
                if slider.knob_rect.collidepoint(event.pos) or slider.track_rect.collidepoint(event.pos):
                    self.dragging_slider = slider_key
                    slider.set_from_position(event.pos[0])
                    self._sync_settings_from_sliders()
                    break

        if event.type == pygame.MOUSEMOTION and self.dragging_slider is not None:
            slider = self.sliders[self.dragging_slider]
            slider.set_from_position(event.pos[0])
            self._sync_settings_from_sliders()

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_slider = None

        return False

    def draw_configuration(self, screen, elapsed_ms):
        width, height = screen.get_size()
        self._draw_background(screen, width, height, elapsed_ms)

        frame_rect = pygame.Rect(28, 24, width - 56, height - 48)
        panel = pygame.Rect(frame_rect.left + 24, frame_rect.top + 58, frame_rect.width - 48, frame_rect.height - 96)

        pygame.draw.rect(screen, self.line_color, frame_rect, 2)
        pygame.draw.rect(screen, self.line_color, panel, 1)

        title_surface = self.header_font.render(f"{self.title} :: GRID CONFIG", True, self.glow_color)
        screen.blit(title_surface, (frame_rect.left + 20, frame_rect.top + 18))

        hint_surface = self.small_font.render("DRAG SLIDERS, THEN PRESS ENTER OR CLICK BOOT", True, self.dim_text_color)
        screen.blit(hint_surface, (panel.left + 16, panel.top + 18))

        slider_colors = {
            "glow": self.glow_color,
            "line": self.line_color,
            "fill": (45, 170, 45),
            "dim": self.dim_text_color,
        }

        self.sliders["grid_size"].draw(
            screen,
            panel.left + 20,
            panel.top + 64,
            panel.width - 40,
            self.body_font,
            self.small_font,
            slider_colors,
        )
        self._sync_settings_from_sliders()

        preview_lines = [
            f"PREVIEW GRID      : {self.grid_settings['width']} x {self.grid_settings['height']}",
            f"GRID PIXELS       : {self.grid_settings['grid_pixel_width']} x {self.grid_settings['grid_pixel_height']}",
        ]

        preview_y = panel.top + 170
        for line in preview_lines:
            preview_surface = self.body_font.render(line, True, self.dim_text_color)
            screen.blit(preview_surface, (panel.left + 20, preview_y))
            preview_y += 30

        self.start_button_rect = pygame.Rect(panel.right - 190, panel.bottom - 64, 170, 42)
        pygame.draw.rect(screen, self.line_color, self.start_button_rect, 2)
        btn_text = self.body_font.render("BOOT", True, self.glow_color)
        screen.blit(
            btn_text,
            (
                self.start_button_rect.centerx - (btn_text.get_width() // 2),
                self.start_button_rect.centery - (btn_text.get_height() // 2),
            ),
        )

    def draw(self, screen, progress_steps, elapsed_ms):
        width, height = screen.get_size()
        self._draw_background(screen, width, height, elapsed_ms)

        frame_rect = pygame.Rect(28, 24, width - 56, height - 48)
        left_panel = pygame.Rect(frame_rect.left + 20, frame_rect.top + 58, (frame_rect.width // 2) - 30, frame_rect.height - 96)
        right_panel = pygame.Rect(left_panel.right + 20, left_panel.top, frame_rect.right - left_panel.right - 40, left_panel.height)

        pygame.draw.rect(screen, self.line_color, frame_rect, 2)
        pygame.draw.rect(screen, self.line_color, left_panel, 1)
        pygame.draw.rect(screen, self.line_color, right_panel, 1)

        title_surface = self.header_font.render(f"{self.title} :: BOOT SEQUENCE", True, self.glow_color)
        screen.blit(title_surface, (frame_rect.left + 20, frame_rect.top + 18))

        self._draw_left_panel(screen, left_panel, progress_steps, elapsed_ms)
        self._draw_right_panel(screen, right_panel, elapsed_ms)

    def _draw_background(self, screen, width, height, elapsed_ms):
        screen.fill(self.bg_color)

        for x in range(0, width, 28):
            pygame.draw.line(screen, self.panel_color, (x, 0), (x, height), 1)
        for y in range(0, height, 24):
            pygame.draw.line(screen, self.panel_color, (0, y), (width, y), 1)

        # Animated scanline to emulate old terminal refresh.
        scan_y = (elapsed_ms // 5) % height
        pygame.draw.line(screen, (25, 90, 25), (0, scan_y), (width, scan_y), 2)

    def _draw_left_panel(self, screen, panel, progress_steps, elapsed_ms):
        progress = min(1.0, max(0.0, progress_steps / self.total_init_steps))
        spinner = "-|\\/"[(elapsed_ms // 150) % 4]

        info_lines = [
            f"GRID SIZE      : {self.grid_settings['width']} x {self.grid_settings['height']}",
            f"GRID PIXELS    : {self.grid_settings['grid_pixel_width']} x {self.grid_settings['grid_pixel_height']}",
            f"INIT STEP      : {progress_steps}/{self.total_init_steps}",
            f"STATUS         : LOADING {spinner}",
        ]

        y = panel.top + 18
        subtitle = self.body_font.render("SYSTEM SETTINGS", True, self.glow_color)
        screen.blit(subtitle, (panel.left + 14, y))
        y += 36

        for line in info_lines:
            text_surface = self.body_font.render(line, True, self.dim_text_color)
            screen.blit(text_surface, (panel.left + 14, y))
            y += 28

        bar_rect = pygame.Rect(panel.left + 14, panel.bottom - 56, panel.width - 28, 24)
        fill_width = int((bar_rect.width - 4) * progress)
        fill_rect = pygame.Rect(bar_rect.left + 2, bar_rect.top + 2, fill_width, bar_rect.height - 4)

        pygame.draw.rect(screen, self.line_color, bar_rect, 2)
        pygame.draw.rect(screen, (45, 170, 45), fill_rect)

        pct_text = self.small_font.render(f"{int(progress * 100):3d}%", True, self.glow_color)
        screen.blit(pct_text, (bar_rect.right - 44, bar_rect.top - 20))

    def _sync_settings_from_sliders(self):
        grid_size = self.sliders["grid_size"].value
        self.grid_settings["width"] = grid_size
        self.grid_settings["height"] = grid_size

    def _draw_right_panel(self, screen, panel, elapsed_ms):
        header = self.body_font.render("ASCII PIP-UNIT", True, self.glow_color)
        screen.blit(header, (panel.left + 14, panel.top + 18))

        y = panel.top + 56
        jitter = (elapsed_ms // 250) % 2

        for index, line in enumerate(self.ascii_art):
            color = self.glow_color if (index + jitter) % 2 == 0 else self.dim_text_color
            text_surface = self.body_font.render(line, True, color)
            screen.blit(text_surface, (panel.left + 14, y))
            y += 18

        footer = self.small_font.render("TIP: WAIT UNTIL MAP BOOT COMPLETES", True, self.dim_text_color)
        screen.blit(footer, (panel.left + 14, panel.bottom - 34))
