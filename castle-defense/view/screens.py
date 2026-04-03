import pygame
from utils.constants import *

class StartScreen:
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 30)

        self.player1_name = ""
        self.player2_name = ""
        self.active_input = 1

        self.selected_avatar = "knight"
        self.selected_enemy = "troll1"
        self.selected_castle = "castle1"

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.active_input == 1:
                if event.key == pygame.K_RETURN:
                    self.active_input = 2
                elif event.key == pygame.K_BACKSPACE:
                    self.player1_name = self.player1_name[:-1]
                else:
                    self.player1_name += event.unicode

            elif self.active_input == 2:
                if event.key == pygame.K_RETURN:
                    return True  # terminar
                elif event.key == pygame.K_BACKSPACE:
                    self.player2_name = self.player2_name[:-1]
                else:
                    self.player2_name += event.unicode

        return False

    def draw(self, screen):
        screen.fill(BLACK)

        text1 = self.font.render(f"P1: {self.player1_name}", True, WHITE)
        text2 = self.font.render(f"P2: {self.player2_name}", True, WHITE)

        screen.blit(text1, (100, 200))
        screen.blit(text2, (100, 250))

        pygame.display.flip()