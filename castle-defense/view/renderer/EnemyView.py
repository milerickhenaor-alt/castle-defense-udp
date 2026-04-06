import os
import pygame
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class EnemyView:
    # Diccionario de clase (Cache Global) para evitar tirones de pantalla
    _SPRITE_CACHE = {}

    def __init__(self, enemy):
        self.team = enemy.team
        self.size = (80, 80) # Tamaño aumentado como pediste
        
        # Carga las animaciones solo si no están en el cache
        if not EnemyView._SPRITE_CACHE:
            self._load_global_cache()

        self.frame_index = 0
        self.image = None
        
        # 🔥 CORRECCIÓN: Ahora le pasamos 'enemy' a la llamada inicial
        self.update(enemy) 

    def _load_global_cache(self):
        """Carga todas las imágenes en RAM una sola vez"""
        base = os.path.join(BASE_PATH, "assets", "images", "enemies", "trolls", "1")
        actions = ["walk", "attack", "hurt", "die"]
        
        for action in actions:
            path = os.path.join(base, action)
            frames = SpriteLoader.load_animation(path)
            
            # Guardamos versión normal (Equipo A) y volteada (Equipo B)
            EnemyView._SPRITE_CACHE[f"{action}_A"] = [
                pygame.transform.scale(img, self.size).convert_alpha() for img in frames
            ]
            EnemyView._SPRITE_CACHE[f"{action}_B"] = [
                pygame.transform.flip(pygame.transform.scale(img, self.size), True, False).convert_alpha() 
                for img in frames
            ]

    def update(self, enemy):
        """
        Actualiza el frame de la animación basado en el estado del enemigo (walking/attacking).
        """
        # Obtenemos el estado (por defecto 'walk' si no existe)
        state_key = "attack" if getattr(enemy, "state", "walking") == "attacking" else "walk"
        
        anim_key = f"{state_key}_{self.team}"
        frames = EnemyView._SPRITE_CACHE.get(anim_key, [])
        
        if frames:
            # Velocidad de animación: el ataque suele ser un poco más rápido visualmente
            anim_speed = 0.15 if state_key == "attack" else 0.1
            self.frame_index = (self.frame_index + anim_speed) % len(frames)
            self.image = frames[int(self.frame_index)]

    def draw(self, screen, enemy):
        if self.image:
            # ESTO ES VITAL: centrar el dibujo en la coordenada X, Y
            # Así, si el troll mide 80px, 40px quedan a la izquierda y 40px a la derecha de 'enemy.x'
            rect = self.image.get_rect(center=(int(enemy.x), int(enemy.y)))
            screen.blit(self.image, rect)
        # Barra de vida
        bar_w, bar_h = 50, 6
        hp_ratio = enemy.hp / enemy.max_hp if enemy.max_hp > 0 else 0
        pygame.draw.rect(screen, (255, 0, 0), (enemy.x - bar_w//2, enemy.y - 50, bar_w, bar_h))
        pygame.draw.rect(screen, (0, 255, 0), (enemy.x - bar_w//2, enemy.y - 50, bar_w * hp_ratio, bar_h))