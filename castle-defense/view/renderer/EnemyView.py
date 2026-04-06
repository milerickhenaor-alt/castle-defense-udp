import os
import pygame
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class EnemyView:
    # Cache Global: Ahora guarda { "troll1_walk_A": [frames], "troll2_walk_A": [frames] }
    _SPRITE_CACHE = {}

    def __init__(self, enemy):
        self.team = enemy.team
        self.size = (80, 80)
        
        # 🔥 SOLUCIÓN MONSTRUOS IGUALES: Extraer el número del tipo (Ej: "Troll 2" -> "2")
        # Si tu objeto enemy no tiene .type, asegúrate de que el GameState se lo asigne
        self.enemy_type_num = str(getattr(enemy, "type", "1")).split(" ")[-1]
        
        # Cargamos el cache específico para este tipo de troll si no existe
        self._load_type_cache(self.enemy_type_num)

        self.frame_index = 0
        self.image = None
        self.update(enemy) 

    def _load_type_cache(self, type_num):
        """Carga las imágenes del troll específico (1, 2, etc.)"""
        actions = ["walk", "attack", "hurt", "die"]
        base = os.path.join(BASE_PATH, "assets", "images", "enemies", "trolls", type_num)

        for action in actions:
            cache_key = f"troll{type_num}_{action}_{self.team}"
            if cache_key not in EnemyView._SPRITE_CACHE:
                path = os.path.join(base, action)
                frames = SpriteLoader.load_animation(path)
                
                if self.team == "A":
                    processed = [pygame.transform.scale(img, self.size).convert_alpha() for img in frames]
                else:
                    processed = [pygame.transform.flip(pygame.transform.scale(img, self.size), True, False).convert_alpha() for img in frames]
                
                EnemyView._SPRITE_CACHE[cache_key] = processed

    def update(self, enemy):
        state_key = "attack" if getattr(enemy, "state", "walking") == "attacking" else "walk"
        # Usamos la llave específica del tipo de troll
        anim_key = f"troll{self.enemy_type_num}_{state_key}_{self.team}"
        frames = EnemyView._SPRITE_CACHE.get(anim_key, [])
        
        if frames:
            anim_speed = 0.15 if state_key == "attack" else 0.1
            self.frame_index = (self.frame_index + anim_speed) % len(frames)
            self.image = frames[int(self.frame_index)]

    def draw(self, screen, enemy):
        if self.image:
            rect = self.image.get_rect(center=(int(enemy.x), int(enemy.y)))
            screen.blit(self.image, rect)
        
        # Barra de vida
        bar_w, bar_h = 50, 6
        hp_ratio = enemy.hp / enemy.max_hp if enemy.max_hp > 0 else 0
        pygame.draw.rect(screen, (255, 0, 0), (enemy.x - bar_w//2, enemy.y - 50, bar_w, bar_h))
        pygame.draw.rect(screen, (0, 255, 0), (enemy.x - bar_w//2, enemy.y - 50, bar_w * hp_ratio, bar_h))