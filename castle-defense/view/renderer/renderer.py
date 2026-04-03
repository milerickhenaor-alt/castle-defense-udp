import pygame
from view.renderer.PlayerView import PlayerView
from view.renderer.EnemyView import EnemyView
from view.renderer.CastleView import CastleView

class Renderer:
    def __init__(self, screen, selections):
        self.screen = screen

        self.player_views = [
        PlayerView(p) for p in selections["players"]
        ]

        self.enemy_view = EnemyView(selections["enemy"])
        self.castle_view = CastleView(selections["castle"])

    def render(self, game_state):
        self.screen.fill((0,0,0))

        # Castillos
        self.castle_view.draw(self.screen, game_state.castle_left)
        self.castle_view.draw(self.screen, game_state.castle_right)

        # Jugadores
        for i, player in enumerate(game_state.players):
            self.player_views[i].draw(self.screen, player)

        # Enemigos
        for enemy in game_state.enemies:
            self.enemy_view.draw(self.screen, enemy)

        pygame.display.flip()