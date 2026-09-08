"""graphical output pygame engine"""

import pygame
from models import Graph
from simulation import Simulation


class Visualizer:
    def __init__(self, simulation: Simulation, graph: Graph) -> None:
        pygame.init()
        self.simulation: Simulation = simulation
        self.graph: Graph = graph
        # creating canvas
        self.screen: pygame.Surface = pygame.display.set_mode((1400, 800))
        pygame.display.set_caption("Visualizer")
        # clock tracker
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.is_running: bool = True
        # init default font. SysFont(fontnamestring, font scale size)
        self.font: pygame.font.Font = pygame.font.SysFont(None, 15)

    def resolve_color(self, parsed_color_name: str) -> pygame.Color:
        """converting map color into a pygame.Color object"""
        clean_name = parsed_color_name.lower().strip()
        try:
            return pygame.Color(clean_name)
        except ValueError:
            return pygame.Color("white")

    def process_events(self) -> None:
        """listens for user events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                elif event.key == pygame.K_SPACE:
                    total_drones = len(self.simulation.drones)
                    end_zone = self.graph.zones[self.simulation.end_hub_name]
                    if end_zone.current_drones < total_drones:
                        self.simulation.step_turn()

    def _get_map_extremes(self) -> tuple[float, float, float, float]:
        """reads zone coords to find the edges of the map"""
        all_x_coords = [zone.x for zone in self.graph.zones.values()]
        all_y_coords = [zone.y for zone in self.graph.zones.values()]
        if not all_x_coords or not all_y_coords:
            return 0.0, 10.0, 0.0, 10.0
        return (min(all_x_coords),
                max(all_x_coords),
                min(all_y_coords),
                max(all_y_coords))

    def to_screen_pixels(self, raw_x: float, raw_y: float) -> tuple[int, int]:
        """converting map coords into window pixels after padding"""
        x_min, x_max, y_min, y_max = self._get_map_extremes()
        x_span = x_max - x_min
        y_span = y_max - y_min
        # safeguard 0 division
        if x_span == 0:
            x_span = 1.0
        if y_span == 0:
            y_span = 1.0
        padding_x = 100
        padding_y = 120
        x_percentage = (raw_x - x_min) / x_span
        y_percentage = (raw_y - y_min) / y_span
        pixel_x = padding_x + int(x_percentage * (1400 - (2 * padding_x)))
        pixel_y = 800 - padding_y - int(y_percentage * (800 - (2 * padding_y)))
        return pixel_x, pixel_y

    def draw(self) -> None:
        # cleaning after every frame
        self.screen.fill((30, 30, 30))
        # layer 1 drawing connections lines
        for pair_tuple, conn_obj in self.graph.connections.items():
            zone_a_name, zone_b_name = pair_tuple
            zone_a = self.graph.zones[zone_a_name]
            zone_b = self.graph.zones[zone_b_name]
            start_pixels = self.to_screen_pixels(zone_a.x, zone_a.y)
            end_pixels = self.to_screen_pixels(zone_b.x, zone_b.y)
            # pygame.draw.line(surface, color, start_pos, end_pos, width)
            pygame.draw.line(self.screen,
                             (100, 100, 100),
                             start_pixels,
                             end_pixels,
                             3)
            mid_x = (start_pixels[0] + end_pixels[0]) // 2
            mid_y = (start_pixels[1] + end_pixels[1]) // 2
            flight_str = (f"{conn_obj.current_drones} / "
                          f"{conn_obj.max_link_capacity}")
            flight_surface = self.font.render(flight_str,
                                              True,
                                              pygame.Color("white"))
            flight_rect = flight_surface.get_rect()
            flight_rect.center = (mid_x, mid_y + 18)
            self.screen.blit(flight_surface, flight_rect)
        # layer 2 drawing zone circles
        for zone_obj in self.graph.zones.values():
            pixel_x, pixel_y = self.to_screen_pixels(zone_obj.x, zone_obj.y)
            node_color = self.resolve_color(zone_obj.color_name)
            # pygame.draw.circle(self.screen, color, center, radius)
            pygame.draw.circle(self.screen,
                               pygame.Color("black"),
                               (pixel_x, pixel_y),
                               30)
            pygame.draw.circle(self.screen, node_color, (pixel_x, pixel_y), 28)
            # layer 3 Text strings
            # font.render(text, antialias, color)
            capitalized_name = zone_obj.name.upper()
            text_surface = self.font.render(capitalized_name,
                                            True,
                                            pygame.Color("white"))
            # get a rectangle box of the text size and center it
            text_rect = text_surface.get_rect()
            text_rect.center = (pixel_x, pixel_y - 10)
            # text border
            border_surface = self.font.render(capitalized_name,
                                              True,
                                              pygame.Color("black"))
            self.screen.blit(border_surface,
                             (text_rect.x - 1,
                              text_rect.y))
            self.screen.blit(border_surface,
                             (text_rect.x + 1,
                              text_rect.y))
            self.screen.blit(border_surface,
                             (text_rect.x,
                              text_rect.y - 1))
            self.screen.blit(border_surface,
                             (text_rect.x,
                              text_rect.y + 1))
            # copy text surface onto screen bg rect box. blit(source, dest)
            self.screen.blit(text_surface, text_rect)
            # 3.b drone count text
            if zone_obj.identity_type in ("start_hub", "end_hub"):
                count_str = f"Drones: {zone_obj.current_drones}"
            else:
                count_str = (f"{zone_obj.current_drones} / "
                             f"{zone_obj.max_drones}")
            count_surface = self.font.render(count_str,
                                             True,
                                             pygame.Color("white"))
            count_rect = count_surface.get_rect()
            count_rect.center = (pixel_x, pixel_y + 10)
            cnt_border_surface = self.font.render(count_str,
                                                  True,
                                                  pygame.Color("black"))
            self.screen.blit(cnt_border_surface,
                             (count_rect.x - 1,
                              count_rect.y))
            self.screen.blit(cnt_border_surface,
                             (count_rect.x + 1,
                              count_rect.y))
            self.screen.blit(cnt_border_surface,
                             (count_rect.x,
                              count_rect.y - 1))
            self.screen.blit(cnt_border_surface,
                             (count_rect.x,
                              count_rect.y + 1))
            self.screen.blit(count_surface, count_rect)
        # layer 3.c counter display
        turn_text = f"Sim turn: {self.simulation.current_turn}"
        turn_surface = self.font.render(turn_text,
                                        True,
                                        pygame.Color("yellow"))
        self.screen.blit(turn_surface, (20, 20))
        # sim ending message
        total_drones = len(self.simulation.drones)
        end_zone = self.graph.zones[self.simulation.end_hub_name]
        if end_zone.current_drones >= total_drones:
            end_msg = "SIMULATION COMPLETE! PRESS ESC TO EXIT"
            end_surf = self.font.render(end_msg, True, pygame.Color("green"))
            end_rect = end_surf.get_rect()
            end_rect.topright = (1380, 20)
            self.screen.blit(end_surf, end_rect)
        # displaying whats in the current buffer
        pygame.display.flip()

    def run(self) -> None:
        """main visualizer loop"""
        while self.is_running:
            self.process_events()
            self.draw()
            # locking frames at 60
            self.clock.tick(60)
        pygame.quit()
