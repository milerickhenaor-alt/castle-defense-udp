import pygame
import os
from view.renderer.PlayerView import PlayerView
from view.renderer.EnemyView import EnemyView
from view.renderer.CastleView import CastleView

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class Renderer:
    def __init__(self, screen, selections):
        self.screen = screen
        
        # --- 1. Fondo optimizado ---
        bg_path = os.path.join(BASE_PATH, "assets", "images", "background", "Background.png")
        try:
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (1000, 600))
        except Exception as e:
            print(f"Error cargando fondo: {e}")
            self.background = pygame.Surface((1000, 600))
            self.background.fill((30, 30, 30))

        # --- 2. Vistas de Jugadores ---
        # selections["players"] ahora es la lista de 4 objetos Player que mandamos desde el main
        self.player_views = [PlayerView(p) for p in selections["players"]]

        # --- 3. Vistas de Castillos dinámicas ---
        # Tomamos las variantes reales enviadas por el servidor
        self.castle_views = {
            "A": CastleView({"variant": selections.get("castle_a", "1")}),
            "B": CastleView({"variant": selections.get("castle_b", "1")}),
        }

        # --- 4. Vistas de Enemigos ---
        self.enemy_views = {}

    def render(self, game_state):
        # 1. Dibujar Fondo
        self.screen.blit(self.background, (0, 0))

        # 2. Dibujar Castillos
        for team, castle in game_state.castles.items():
            if team in self.castle_views:
                self.castle_views[team].draw(self.screen, castle)

        # 3. Dibujar Jugadores
        # Usamos values() porque en GameState los jugadores suelen estar en un dict por nombre
        for i, player in enumerate(game_state.players.values()):
            if i < len(self.player_views):
                view = self.player_views[i]
                view.update()
                view.draw(self.screen, player.x, player.y, player.team)

        # 4. Dibujar Enemigos (Mantenemos tu lógica exacta)
        alive_ids = set()
        for enemy in game_state.enemies:
            alive_ids.add(enemy.id)
            
            # Si no existe la vista para este ID, la creamos
            if enemy.id not in self.enemy_views:
                self.enemy_views[enemy.id] = EnemyView(enemy)
            
            view = self.enemy_views[enemy.id]
            
            # FIX: Le pasamos el objeto 'enemy' para que sepa si atacar o caminar
            view.update(enemy) 
            view.draw(self.screen, enemy)

        # 5. Limpieza de memoria (Enemigos que ya no están en el estado)
        if len(self.enemy_views) > len(alive_ids):
            self.enemy_views = {
                eid: ev for eid, ev in self.enemy_views.items() if eid in alive_ids
            }