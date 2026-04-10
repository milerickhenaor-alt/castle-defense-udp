import os
import pygame
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class EnemyView:
    def __init__(self, enemy, enemy_type):
        self.enemy_type = enemy_type

        # 🔥 EXTRAER SOLO EL NÚMERO (Ej: "Troll 1" → "1")
        number = str(enemy_type).split(" ")[-1]

        # 🔥 RUTA REAL SEGÚN TU PROYECTO
        self.base_path = os.path.join(
            BASE_PATH, "assets", "images", "enemies", "trolls", number
        )

        print(f"📂 Cargando enemigo desde: {self.base_path}")

        # --- CARGA DE ANIMACIONES ---
        try:
            self.walk_frames = SpriteLoader.load_animation(
                os.path.join(self.base_path, "walk")
            )
            self.attack_frames = SpriteLoader.load_animation(
                os.path.join(self.base_path, "attack")
            )
        except Exception as e:
            print(f"❌ Error cargando animaciones: {e}")
            self.walk_frames = []
            self.attack_frames = []

        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = None

    def update(self, enemy):
        frames = self.attack_frames if enemy.state == "attacking" else self.walk_frames

        if frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(frames):
                self.frame_index = 0

            self.image = frames[int(self.frame_index)]
        else:
            self.image = None

    def draw(self, screen, enemy):
        if not self.image:
            pygame.draw.rect(screen, (255, 0, 0), (enemy.x - 20, enemy.y - 20, 40, 40))
            return

        img = self.image

        if enemy.team == "B":
            img = pygame.transform.flip(img, True, False)

        img = pygame.transform.scale(img, (70, 70))
        rect = img.get_rect(center=(int(enemy.x), int(enemy.y)))
        screen.blit(img, rect)