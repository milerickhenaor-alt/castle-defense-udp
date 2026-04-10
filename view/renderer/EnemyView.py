import os
import pygame
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class EnemyView:
    def __init__(self, enemy):
        # enemy.type suele ser "Troll 1" o "Troll 2"
        self.base_path = os.path.join(BASE_PATH, "assets", "images", "enemies", enemy.type)
        
        # Cargamos las dos animaciones posibles
        self.walk_frames = SpriteLoader.load_animation(os.path.join(self.base_path, "walk"))
        self.attack_frames = SpriteLoader.load_animation(os.path.join(self.base_path, "attack"))
        
        self.frame_index = 0
        self.animation_speed = 0.15

    def update(self, enemy):
        # Elegir animación según el estado del modelo
        frames = self.attack_frames if enemy.state == "attacking" else self.walk_frames
        
        if frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(frames):
                self.frame_index = 0
            self.image = frames[int(self.frame_index)]
        else:
            # Fallback: superficie roja si no hay imágenes
            self.image = pygame.Surface((40, 40))
            self.image.fill((255, 0, 0))

    def draw(self, screen, enemy):
        # Voltear imagen si el equipo es B (vienen de la derecha)
        img = self.image
        if enemy.team == "B":
            img = pygame.transform.flip(img, True, False)
        
        # Escalar enemigo
        img = pygame.transform.scale(img, (60, 60))
        rect = img.get_rect(center=(int(enemy.x), int(enemy.y)))
        screen.blit(img, rect)