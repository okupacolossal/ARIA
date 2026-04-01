import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

# Amber phosphor palette
A1  = (255, 208,  82)   # bright amber
A2  = (220, 155,  35)   # mid amber
A3  = (175, 118,  28)   # border
A4  = (132,  92,  30)   # dim
A5  = ( 48,  32,   5)   # very dark
BG  = (  9,   7,   5)   # background


def show_end_game_screen(screen: pygame.Surface, clock: pygame.time.Clock, overall_stats: dict) -> None:
    """Display end-game statistics and recommended station location."""
    
    # Fonts
    title_font = pygame.font.SysFont("couriernew", 28, bold=True)
    header_font = pygame.font.SysFont("couriernew", 16, bold=True)
    body_font = pygame.font.SysFont("couriernew", 13)
    small_font = pygame.font.SysFont("couriernew", 11)
    
    width, height = screen.get_size()
    
    # Event loop for end screen
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                # Any key to exit
                return
        
        # Draw background
        screen.fill(BG)
        
        # Draw title
        title_surf = title_font.render("SIMULATION COMPLETE", True, A1)
        title_rect = title_surf.get_rect(center=(width // 2, 40))
        screen.blit(title_surf, title_rect)
        
        # Draw divider
        pygame.draw.line(screen, A3, (40, 70), (width - 40, 70), 2)
        
        # Stats panel
        y_offset = 100
        line_height = 28
        
        # Total generations
        gen_text = body_font.render(
            f"Total Generations: {overall_stats['total_generations']:03d}",
            True, A2
        )
        screen.blit(gen_text, (60, y_offset))
        y_offset += line_height
        
        # Total deaths
        deaths_text = body_font.render(
            f"Total Deaths: {overall_stats['total_deaths']:05d}",
            True, A2
        )
        screen.blit(deaths_text, (60, y_offset))
        y_offset += line_height
        
        # Total ambulances dispatched
        amb_text = body_font.render(
            f"Ambulances Dispatched: {overall_stats['total_ambulances']:05d}",
            True, A2
        )
        screen.blit(amb_text, (60, y_offset))
        y_offset += line_height
        
        # Average deaths per generation
        avg_deaths_text = body_font.render(
            f"Average Deaths/Gen: {overall_stats['average_deaths_per_gen']:.1f}",
            True, A4
        )
        screen.blit(avg_deaths_text, (60, y_offset))
        y_offset += line_height
        
        # Mortality rate
        mortality_text = body_font.render(
            f"Mortality Rate: {overall_stats['mortality_rate']*100:.1f}%",
            True, A4
        )
        screen.blit(mortality_text, (60, y_offset))
        y_offset += line_height * 1.5
        
        # Divider
        pygame.draw.line(screen, A3, (40, y_offset - 10), (width - 40, y_offset - 10), 1)
        y_offset += 20
        
        # Recommended station location
        header_text = header_font.render("RECOMMENDED NEW STATION LOCATION", True, A1)
        screen.blit(header_text, (60, y_offset))
        y_offset += line_height
        
        if overall_stats['best_station_location']:
            best_lat, best_lon = overall_stats['best_station_location']
            
            lat_text = small_font.render(
                f"Latitude:  {best_lat:.6f}",
                True, A2
            )
            screen.blit(lat_text, (80, y_offset))
            y_offset += 24
            
            lon_text = small_font.render(
                f"Longitude: {best_lon:.6f}",
                True, A2
            )
            screen.blit(lon_text, (80, y_offset))
            y_offset += 24
            
            # Explanation
            info_text = small_font.render(
                "Based on average mortality hotspot from all generations",
                True, A4
            )
            screen.blit(info_text, (80, y_offset))
        else:
            msg_text = body_font.render("No data available", True, A4)
            screen.blit(msg_text, (80, y_offset))
        
        y_offset += line_height * 2
        
        # Instructions
        pygame.draw.line(screen, A3, (40, y_offset), (width - 40, y_offset), 1)
        y_offset += 20
        
        instr_text = small_font.render("Press any key to exit", True, A4)
        instr_rect = instr_text.get_rect(center=(width // 2, y_offset))
        screen.blit(instr_text, instr_rect)
        
        pygame.display.flip()
        clock.tick(30)
