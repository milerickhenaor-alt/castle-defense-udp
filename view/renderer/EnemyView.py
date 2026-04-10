import pygame
import os
from view.renderer.PlayerView import PlayerView
from view.renderer.CastleView import CastleView

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class Renderer:
    def __init__(self, screen, selections):
        self.screen = screen
        
        # --- Fondo ---
        try:
            bg_path = os.path.join(BASE_PATH, "assets", "images", "background", "Background.png")
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (1000, 600))
        except:
            self.background = pygame.Surface((1000, 600))
            self.background.fill((30, 30, 30))

        # --- Jugadores ---
        self.player_views = {}
        if "players" in selections:
            for p in selections["players"]:
                self.player_views[p.name] = PlayerView(p)

        # --- Castillos ---
        self.castle_views = {
            "A": CastleView({"variant": str(selections.get("castle_a", "1"))}),
            "B": CastleView({"variant": str(selections.get("castle_b", "1"))}),
        }

        self.enemy_views = {}

    def render(self, game_state):
        # 1. Dibujar Fondo
        self.screen.blit(self.background, (0, 0))

        # 2. Dibujar Castillos
        for team, castle in game_state.castles.items():
            if team in self.castle_views:
                self.castle_views[team].draw(self.screen, castle)

        # 3. Dibujar Jugadores
        for player in game_state.players.values():
            if player.name not in self.player_views:
                self.player_views[player.name] = PlayerView(player)
            
            view = self.player_views[player.name]
            view.update()
            view.draw(self.screen, player.x, player.y, player.team)

        # 4. Dibujar Enemigos (Monstruos)
        current_enemy_ids = set()
        for enemy in game_state.enemies:
            current_enemy_ids.add(enemy.id)

            if enemy.id not in self.enemy_views:
                self.enemy_views[enemy.id] = EnemyView(enemy)

            view = self.enemy_views[enemy.id]
            view.update(enemy)
            view.draw(self.screen, enemy)

        # Limpiar vistas de enemigos que ya no están en el modelo (muertos)
        self.enemy_views = {eid: ev for eid, ev in self.enemy_views.items() if eid in current_enemy_ids}