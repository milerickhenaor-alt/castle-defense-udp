import pygame
from utils.constants import *

class GameOverScreen:
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont(FONT_NAME, FONT_LARGE)

    def draw(self, screen, game_state):
        screen.fill(BLACK)

        winner = "Team A" if game_state.score_left > game_state.score_right else "Team B"

        title = self.font.render("GAME OVER", True, WHITE)
        result = self.font.render(f"Winner: {winner}", True, GREEN)

        score = self.font.render(
            f"{game_state.score_left} - {game_state.score_right}",
            True, WHITE
        )

        screen.blit(title, (SCREEN_WIDTH//2 - 120, 150))
        screen.blit(result, (SCREEN_WIDTH//2 - 120, 250))
        screen.blit(score, (SCREEN_WIDTH//2 - 80, 320))

        pygame.display.flip()