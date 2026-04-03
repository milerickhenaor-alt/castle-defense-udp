import pygame
import os
from utils.constants import *

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class StartScreen:
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont(FONT_NAME, FONT_MEDIUM)

        # NOMBRES
        self.player1_name = ""
        self.player2_name = ""
        self.input_active = 1

        self.mode = "name"

        # PLAYERS
        self.avatars = [
            ("Fairies", "1"), ("Fairies", "2"), ("Fairies", "3"),
            ("gentlemen", "1"), ("gentlemen", "2"), ("gentlemen", "3"),
            ("Warrior", "1"), ("Warrior", "2"), ("Warrior", "3"),
        ]

        self.avatar_index = 0
        self.selected_players = []

        self.avatar_images = []
        for name, number in self.avatars:
            path = os.path.join(BASE_PATH, "assets", "images", "players", f"{name}{number}.png")
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (80, 80))
            self.avatar_images.append(img)

        # 👹 TROLLS
        self.trolls = ["1", "2", "3"]
        self.troll_index = 0
        self.selected_enemy = None

        self.troll_images = []
        for i in self.trolls:
            path = os.path.join(BASE_PATH, "assets", "images", "enemies", f"trolls{i}.png")
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (80, 80))
            self.troll_images.append(img)

        # 🏰 CASTILLOS
        self.castles = ["1", "2", "3"]
        self.castle_index = 0
        self.selected_castle = None

        self.castle_images = []
        for i in self.castles:
            path = os.path.join(BASE_PATH, "assets", "images", "castles", f"full{i}.png")
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (100, 100))
            self.castle_images.append(img)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if self.mode == "name":
                if self.input_active == 1:
                    if event.key == pygame.K_RETURN:
                        self.input_active = 2
                    elif event.key == pygame.K_BACKSPACE:
                        self.player1_name = self.player1_name[:-1]
                    else:
                        self.player1_name += event.unicode

                elif self.input_active == 2:
                    if event.key == pygame.K_RETURN:
                        self.mode = "players"
                    elif event.key == pygame.K_BACKSPACE:
                        self.player2_name = self.player2_name[:-1]
                    else:
                        self.player2_name += event.unicode

            elif self.mode == "players":
                if event.key == pygame.K_LEFT:
                    self.avatar_index = (self.avatar_index - 1) % len(self.avatars)

                elif event.key == pygame.K_RIGHT:
                    self.avatar_index = (self.avatar_index + 1) % len(self.avatars)

                elif event.key == pygame.K_RETURN:
                    selected = self.avatars[self.avatar_index]

                    self.selected_players.append({
                        "type": selected[0],
                        "variant": selected[1]
                    })

                    if len(self.selected_players) == 2:
                        self.mode = "enemy"

            elif self.mode == "enemy":
                if event.key == pygame.K_LEFT:
                    self.troll_index = (self.troll_index - 1) % len(self.trolls)

                elif event.key == pygame.K_RIGHT:
                    self.troll_index = (self.troll_index + 1) % len(self.trolls)

                elif event.key == pygame.K_RETURN:
                    self.selected_enemy = self.trolls[self.troll_index]
                    self.mode = "castle"

            elif self.mode == "castle":
                if event.key == pygame.K_LEFT:
                    self.castle_index = (self.castle_index - 1) % len(self.castles)

                elif event.key == pygame.K_RIGHT:
                    self.castle_index = (self.castle_index + 1) % len(self.castles)

                elif event.key == pygame.K_RETURN:
                    self.selected_castle = self.castles[self.castle_index]
                    return True

        return False

    def draw(self, screen):
        screen.fill(BLACK)

        if self.mode == "name":
            screen.blit(self.font.render(f"P1: {self.player1_name}", True, WHITE), (100, 200))
            screen.blit(self.font.render(f"P2: {self.player2_name}", True, WHITE), (100, 250))

        elif self.mode == "players":
            screen.blit(self.font.render(f"Players: {len(self.selected_players)}/2", True, YELLOW), (100, 150))

            for i, img in enumerate(self.avatar_images):
                x = 50 + i * 100
                screen.blit(img, (x, 250))

                if i == self.avatar_index:
                    pygame.draw.rect(screen, YELLOW, (x, 250, 80, 80), 3)

        elif self.mode == "enemy":
            for i, img in enumerate(self.troll_images):
                x = 100 + i * 120
                screen.blit(img, (x, 250))

                if i == self.troll_index:
                    pygame.draw.rect(screen, YELLOW, (x, 250, 80, 80), 3)

        elif self.mode == "castle":
            for i, img in enumerate(self.castle_images):
                x = 100 + i * 140
                screen.blit(img, (x, 250))

                if i == self.castle_index:
                    pygame.draw.rect(screen, YELLOW, (x, 250, 100, 100), 3)

        pygame.display.flip()