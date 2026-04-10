import pygame
import os
from view.renderer.PlayerView import PlayerView
from view.renderer.EnemyView import EnemyView
from view.renderer.CastleView import CastleView

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class Renderer:
    def __init__(self, screen, selections):
        self.screen = screen
        
        # --- Fondo ---
        try:
            bg_path = os.path.join(BASE_PATH, "assets", "images", "background", "Background.png")
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (1000, 600))
        except Exception as e:
            print(f"Error cargando fondo: {e}")
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

        # --- Enemigos ---
        self.enemy_views = {}
        self.enemy_types = selections.get("enemy_types", {})

    def render(self, game_state):

        # --- Fondo ---
        self.screen.blit(self.background, (0, 0))

        # --- Castillos ---
        for team, castle in game_state.castles.items():
            if team in self.castle_views:
                self.castle_views[team].draw(self.screen, castle)

        # --- Jugadores ---
        for player in game_state.players.values():

            if player.name not in self.player_views:
                print(f"Renderer: Creando vista nueva para {player.name}")
                self.player_views[player.name] = PlayerView(player)
            
            view = self.player_views[player.name]
            view.update()
            view.draw(self.screen, player.x, player.y, player.team)

        # --- Enemigos ---
        current_enemy_ids = set()

        # --- 5. PROYECTILES (NUEVO) ---
        for proj in game_state.projectiles:
            if proj.active:
                # Dibujamos usando la vista única
                self.projectile_view.draw(self.screen, proj.x, proj.y, proj.team)

        print("👾 Enemigos recibidos:", len(game_state.enemies))
        for enemy in game_state.enemies:
            print("Enemy:", enemy.id, enemy.x, enemy.y, enemy.type)
            current_enemy_ids.add(enemy.id)

            if enemy.id not in self.enemy_views:
                enemy_type = getattr(enemy, "type", "Troll 1")
                self.enemy_views[enemy.id] = EnemyView(enemy, enemy_type)

            view = self.enemy_views[enemy.id]
            view.update(enemy)
            view.draw(self.screen, enemy)

        # 🔥 FIX IMPORTANTE: limpieza correcta SIEMPRE
        self.enemy_views = {
            eid: ev for eid, ev in self.enemy_views.items()
            if eid in current_enemy_ids
        }

    def draw_ui(self, game_state):
        font = pygame.font.SysFont("Arial", 24, bold=True)
        timer_text = font.render(f"Tiempo: {int(game_state.remaining_time)}s", True, (255, 255, 255))
        self.screen.blit(timer_text, (450, 20))