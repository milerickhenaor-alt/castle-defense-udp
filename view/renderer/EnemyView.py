import os
import pygame
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class EnemyView:
    def __init__(self, enemy):
        # enemy.type viene del servidor (ej: "Troll 1")
        self.enemy_type = enemy.type
        self.base_path = os.path.join(BASE_PATH, "assets", "images", "enemies", self.enemy_type)
        
        # Cargar animaciones de la carpeta del troll específico
        self.walk_frames = SpriteLoader.load_animation(os.path.join(self.base_path, "walk"))
        self.attack_frames = SpriteLoader.load_animation(os.path.join(self.base_path, "attack"))
        
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = None

    def update(self, enemy):
        # Cambiar animación según el estado del enemigo en el modelo
        frames = self.attack_frames if enemy.state == "attacking" else self.walk_frames
        
        if frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(frames):
                self.frame_index = 0
            self.image = frames[int(self.frame_index)]

    def draw(self, screen, enemy):
        if not self.image:
            # Cuadro rojo de debug si fallan los assets del troll
            pygame.draw.rect(screen, (255, 0, 0), (enemy.x-20, enemy.y-20, 40, 40))
            return

        img = self.image
        if enemy.team == "B":
            img = pygame.transform.flip(img, True, False)
        
        img = pygame.transform.scale(img, (70, 70))
        rect = img.get_rect(center=(int(enemy.x), int(enemy.y)))
        screen.blit(img, rect)