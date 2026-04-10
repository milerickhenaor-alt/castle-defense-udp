import pygame
import os
from view.renderer.PlayerView import PlayerView
from view.renderer.EnemyView import EnemyView
from view.renderer.CastleView import CastleView
from view.renderer.ProjectileView import ProjectileView

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
            self.background = pygame.Surface((1000, 600))
            self.background.fill((30, 30, 30))

        self.player_views = {}
        self.enemy_views = {}
        self.castle_views = {
            "A": CastleView({"variant": str(selections.get("castle_a", "1"))}),
            "B": CastleView({"variant": str(selections.get("castle_b", "1"))}),
        }
        
        # Instancia única para proyectiles
        self.projectile_view = ProjectileView()

    def render(self, game_state):
        if not game_state: return

        # 1. Fondo
        self.screen.blit(self.background, (0, 0))

        # 2. Castillos
        for team, castle in game_state.castles.items():
            if team in self.castle_views:
                self.castle_views[team].draw(self.screen, castle)

        # 3. Jugadores
        for player in game_state.players.values():
            if player.name not in self.player_views:
                self.player_views[player.name] = PlayerView(player)
            
            view = self.player_views[player.name]
            view.update()
            view.draw(self.screen, player.x, player.y, player.team)

        # 4. Enemigos
        current_enemy_ids = set()
        for enemy in game_state.enemies:
            current_enemy_ids.add(enemy.id)
            if enemy.id not in self.enemy_views:
                e_type = getattr(enemy, "type", "Troll 1")
                self.enemy_views[enemy.id] = EnemyView(enemy, e_type)

            view = self.enemy_views[enemy.id]
            view.update(enemy)
            view.draw(self.screen, enemy)

        # Limpiar enemigos muertos
        self.enemy_views = {eid: ev for eid, ev in self.enemy_views.items() if eid in current_enemy_ids}

        # 5. Proyectiles (Capa superior)
        if hasattr(game_state, 'projectiles'):
            for proj in game_state.projectiles:
                # Dibujamos solo si el servidor dice que está activo
                if getattr(proj, 'active', True):
                    self.projectile_view.draw(self.screen, proj.x, proj.y, proj.team)

        # 6. Interfaz
        self.draw_ui(game_state)

    def draw_ui(self, game_state):
        font = pygame.font.SysFont("Arial", 22, bold=True)
        # Tiempo
        timer_txt = font.render(f"Tiempo: {int(game_state.remaining_time)}s", True, (255, 255, 255))
        self.screen.blit(timer_txt, (450, 20))