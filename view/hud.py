import pygame

class Hud:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 20)
        self.font_big = pygame.font.SysFont("Arial", 28, bold=True)

    def draw(self, game_state):
        # 1. Tiempo - Centrado en 1000px (500 es la mitad)
        time_left = int(game_state.remaining_time)
        time_text = self.font_big.render(f"Time: {time_left}", True, (255, 255, 255))
        # Centramos el texto restando un poco de X
        self.screen.blit(time_text, (450, 10)) 

        # 2. Barras de Vida
        castle_a = game_state.castles["A"]
        castle_b = game_state.castles["B"]

        # Barra A: Empieza en 20px
        color_a = (0, 200, 0) if castle_a.hp_ratio > 0.3 else (220, 0, 0)
        self.draw_bar(20, 50, 250, 20, castle_a.hp_ratio, color_a)

        # Barra B: Termina en 980px (980 - 250 de ancho = 730)
        color_b = (200, 0, 0) if castle_b.hp_ratio > 0.3 else (255, 128, 0)
        self.draw_bar(730, 50, 250, 20, castle_b.hp_ratio, color_b)

        # 3. Scores - Debajo del tiempo
        score_a = sum(p.score for p in game_state.players.values() if p.team == "A")
        score_b = sum(p.score for p in game_state.players.values() if p.team == "B")
        score_text = self.font_big.render(f"{score_a} - {score_b}", True, (255, 255, 255))
        self.screen.blit(score_text, (470, 60))

    def draw_bar(self, x, y, width, height, ratio, color):
        # Fondo oscuro
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, width, height))
        # Borde blanco fino
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, width, height), 1)
        # Vida
        if ratio > 0:
            pygame.draw.rect(self.screen, color, (x, y, int(width * ratio), height))