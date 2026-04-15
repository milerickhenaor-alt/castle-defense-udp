import pygame
import os
from view.renderer.PlayerView import PlayerView
from view.renderer.EnemyView import EnemyView
from view.renderer.CastleView import CastleView
from view.renderer.ProyectileView import ProjectileView

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class Renderer:
    def __init__(self, screen, selections):
        self.screen = screen
        
        # --- Control de Sonidos (Sets para evitar repetición en cada frame) ---
        self.played_projectiles = set()  # IDs de proyectiles que ya sonaron
        self.enemies_attacking = set()   # IDs de trolls que ya sonaron al atacar

        try:
            pygame.mixer.init()
            self.sound_troll = pygame.mixer.Sound(os.path.join(BASE_PATH, "assets", "sounds", "destruccion.mp3"))
            self.sound_proyectile = pygame.mixer.Sound(os.path.join(BASE_PATH, "assets", "sounds", "disparo.mp3"))
        except:
            print("⚠️ Advertencia: No se encontraron algunos archivos de sonido en assets/sounds/")
        
        # --- Fondo ---
        try:
            bg_path = os.path.join(BASE_PATH, "assets", "images", "background", "Background.png")
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (1000, 600))
        except Exception as e:
            print(f"❌ Error cargando fondo: {e}")
            self.background = pygame.Surface((1000, 600))
            self.background.fill((30, 30, 30))

        # --- Vistas de Entidades ---
        self.player_views = {}
        self.enemy_views = {}
        self.castle_views = {
            "A": CastleView({"variant": str(selections.get("castle_a", "1"))}),
            "B": CastleView({"variant": str(selections.get("castle_b", "1"))}),
        }
        
        # Instancia única para proyectiles
        self.projectile_view = ProjectileView()

    def render(self, game_state):
        if not game_state: 
            return

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

        # 4. Dibujar Enemigos y Sonido de Ataque
        current_enemy_ids = set()
        for enemy in game_state.enemies:
            current_enemy_ids.add(enemy.id)
            
            if enemy.id not in self.enemy_views:
                e_type = getattr(enemy, "type", "Troll 1")
                self.enemy_views[enemy.id] = EnemyView(enemy, e_type)

            # Lógica de sonido de ataque del Troll
            # Se activa si el enemigo está en rango de ataque y no ha sonado para este ciclo
            is_attacking = getattr(enemy, 'is_attacking', False)
            if is_attacking and enemy.id not in self.enemies_attacking:
                try: self.sound_troll.play()
                except: pass
                self.enemies_attacking.add(enemy.id)
            elif not is_attacking:
                # Si deja de atacar (ej. muere o se mueve), permitimos que vuelva a sonar después
                self.enemies_attacking.discard(enemy.id)

            view = self.enemy_views[enemy.id]
            view.update(enemy)
            view.draw(self.screen, enemy)

        # Limpiar vistas de enemigos que ya no existen en el game_state
        self.enemy_views = {eid: ev for eid, ev in self.enemy_views.items() if eid in current_enemy_ids}
        # Limpiar registro de sonidos de ataque para enemigos eliminados
        self.enemies_attacking = {eid for eid in self.enemies_attacking if eid in current_enemy_ids}

        # 5. Dibujar Proyectiles y Sonido de Disparo
        if hasattr(game_state, 'projectiles'):
            current_projectile_ids = set()
            for proj in game_state.projectiles:
                if getattr(proj, 'active', True):
                    current_projectile_ids.add(proj.id)
                    
                    # Sonar SOLO una vez cuando el proyectil aparece
                    if proj.id not in self.played_projectiles:
                        try: self.sound_proyectile.play()
                        except: pass
                        self.played_projectiles.add(proj.id)
                    
                    self.projectile_view.draw(self.screen, proj.x, proj.y, proj.team)
            
            # Limpiar el registro de proyectiles antiguos para no saturar la memoria
            self.played_projectiles = {pid for pid in self.played_projectiles if pid in current_projectile_ids}