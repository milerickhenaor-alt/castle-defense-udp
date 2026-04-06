import pygame
import os
from view.renderer.PlayerView import PlayerView
from view.renderer.EnemyView import EnemyView
from view.renderer.CastleView import CastleView

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class Renderer:
    def __init__(self, screen, selections):
        """
        selections: Diccionario enviado desde el main con 'players', 'castle_a', etc.
        """
        self.screen = screen
        
        # 1. Carga de Fondo
        try:
            bg_path = os.path.join(BASE_PATH, "assets", "images", "background", "Background.png")
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (1000, 600))
        except Exception as e:
            print(f"Error cargando fondo: {e}")
            self.background = pygame.Surface((1000, 600))
            self.background.fill((30, 30, 30))

        # 2. Vistas de Jugadores (Diccionario por nombre para Skins únicas)
        # Se crean inicialmente con los datos del payload de inicio
        self.player_views = {}
        if "players" in selections:
            for p in selections["players"]:
                self.player_views[p.name] = PlayerView(p)

        # 3. Vistas de Castillos
        self.castle_views = {
            "A": CastleView({"variant": str(selections.get("castle_a", "1"))}),
            "B": CastleView({"variant": str(selections.get("castle_b", "1"))}),
        }

        # 4. Contenedor dinámico de Enemigos (Trolls)
        self.enemy_views = {}

    def render(self, game_state):
        """
        Dibuja el estado actual del juego enviado por el servidor o calculado localmente.
        """
        # --- Capa 0: Fondo ---
        self.screen.blit(self.background, (0, 0))

        # --- Capa 1: Castillos ---
        for team, castle in game_state.castles.items():
            if team in self.castle_views:
                self.castle_views[team].draw(self.screen, castle)

        # --- Capa 2: Jugadores (Sincronización por Nombre) ---
        for player in game_state.players.values():
            # Si aparece un jugador nuevo por red que no teníamos, creamos su vista
            if player.name not in self.player_views:
                print(f"Renderer: Creando vista nueva para {player.name}")
                self.player_views[player.name] = PlayerView(player)
            
            view = self.player_views[player.name]
            view.update() # Para animaciones internas (idle/walk)
            # Dibujamos en las coordenadas que vienen del GameState (sincronizadas)
            view.draw(self.screen, player.x, player.y, player.team)

        # --- Capa 3: Enemigos (Sincronización por ID) ---
        current_enemy_ids = set()
        
        for enemy in game_state.enemies:
            current_enemy_ids.add(enemy.id)
            
            # Si el troll es nuevo, creamos su EnemyView (esto detecta si es Troll 1, 2 o 3)
            if enemy.id not in self.enemy_views:
                self.enemy_views[enemy.id] = EnemyView(enemy)
            
            view = self.enemy_views[enemy.id]
            view.update(enemy) # Sincroniza estado de animación
            view.draw(self.screen, enemy)

        # --- Capa 4: Limpieza de Memoria ---
        # Si un troll murió o desapareció del game_state, eliminamos su vista
        if len(self.enemy_views) > len(current_enemy_ids):
            self.enemy_views = {
                eid: ev for eid, ev in self.enemy_views.items() 
                if eid in current_enemy_ids
            }

    def draw_ui(self, game_state):
        """
        Opcional: Si quieres dibujar el tiempo restante o scores aquí
        """
        # Ejemplo: Tiempo
        font = pygame.font.SysFont("Arial", 24, bold=True)
        timer_text = font.render(f"Tiempo: {int(game_state.remaining_time)}s", True, (255, 255, 255))
        self.screen.blit(timer_text, (450, 20))