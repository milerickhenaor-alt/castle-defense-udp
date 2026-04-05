import os
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class EnemyView:

    def __init__(self, enemy_data):
        # 🔥 Extraer datos correctamente
        enemy_type = enemy_data["type"]
        variant = str(enemy_data["variant"])

        base = os.path.join(
            BASE_PATH,
            "assets",
            "images",
            "enemies",
            enemy_type,
            variant
        )

        # 🔥 Cargar animaciones BIEN
        self.walk = SpriteLoader.load_animation(os.path.join(base, "walk"))
        self.attack = SpriteLoader.load_animation(os.path.join(base, "attack"))
        self.hit = SpriteLoader.load_animation(os.path.join(base, "hurt"))
        self.die = SpriteLoader.load_animation(os.path.join(base, "die"))

        self.frame_index = 0

    def draw(self, screen, enemy):
        if not self.walk:
            return

        image = self.walk[self.frame_index % len(self.walk)]

        screen.blit(image, (enemy.x, enemy.y))

        self.frame_index += 1