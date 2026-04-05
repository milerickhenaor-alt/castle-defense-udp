import pygame

class Hud:
    def __init__(self, screen):
        self.screen = screen

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 20)
        self.font_big = pygame.font.SysFont("Arial", 28, bold=True)

    def draw(self, game_state):
        screen = self.screen

        # 🔥 TIEMPO
        time_left = int(game_state.remaining_time)
        time_text = self.font_big.render(f"Time: {time_left}", True, (255, 255, 255))
        screen.blit(time_text, (450, 10))

        # 🔥 VIDA CASTILLOS
        castle_a = game_state.castles["A"]
        castle_b = game_state.castles["B"]

        self.draw_bar(50, 50, 300, 20, castle_a.hp_ratio, (0, 200, 0))
        self.draw_bar(650, 50, 300, 20, castle_b.hp_ratio, (200, 0, 0))

        # 🔥 SCORES
        score_a = sum(p.score for p in game_state.players.values() if p.team == "A")
        score_b = sum(p.score for p in game_state.players.values() if p.team == "B")

        score_text = self.font_big.render(f"{score_a} - {score_b}", True, (255, 255, 255))
        screen.blit(score_text, (480, 80))

        # 🔥 NOMBRES DE JUGADORES ENCIMA
        for player in game_state.players.values():
            name_text = self.font.render(player.name, True, (255, 255, 0))
            screen.blit(name_text, (player.x - 20, player.y - 40))

    def draw_bar(self, x, y, width, height, ratio, color):
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, width, height))
        pygame.draw.rect(self.screen, color, (x, y, width * ratio, height))