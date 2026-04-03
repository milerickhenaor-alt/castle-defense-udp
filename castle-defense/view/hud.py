import pygame
from utils.constants import *

class Hud:
    def __init__(self):
        pygame.font.init()
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.font_medium = pygame.font.SysFont("Arial", 28)

    def draw_time(self, screen, time_left):
        text = self.font_medium.render(f"Time: {int(time_left)}", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - 60, 10))

    def draw_score(self, screen, score_left, score_right):
        text_left = self.font_small.render(f"Team A: {score_left}", True, WHITE)
        text_right = self.font_small.render(f"Team B: {score_right}", True, WHITE)

        screen.blit(text_left, (10, 10))
        screen.blit(text_right, (SCREEN_WIDTH - 150, 10))

    def draw_players(self, screen, players):
        y_offset = 40

        for player in players:
            text = self.font_small.render(player.name, True, WHITE)
            screen.blit(text, (10, y_offset))
            y_offset += 20

    def draw(self, screen, game_state):
        self.draw_time(screen, game_state.time_left)
        self.draw_score(screen, game_state.score_left, game_state.score_right)
        self.draw_players(screen, game_state.players)