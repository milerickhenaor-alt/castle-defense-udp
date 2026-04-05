import pygame
from utils.constants import *

class GameOverScreen:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.SysFont(FONT_NAME, FONT_LARGE)

    def handle_event(self, event):
        pass  # para mantener consistencia

    def draw(self, game_state):
        self.screen.fill(BLACK)

        winner = "Team A" if game_state.score_left > game_state.score_right else "Team B"

        title = self.font.render("GAME OVER", True, WHITE)
        result = self.font.render(f"Winner: {winner}", True, GREEN)

        score = self.font.render(
            f"{game_state.score_left} - {game_state.score_right}",
            True, WHITE
        )

        self.screen.blit(title, (SCREEN_WIDTH//2 - 120, 150))
        self.screen.blit(result, (SCREEN_WIDTH//2 - 120, 250))
        self.screen.blit(score, (SCREEN_WIDTH//2 - 80, 320))