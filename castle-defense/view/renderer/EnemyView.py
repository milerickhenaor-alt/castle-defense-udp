import os
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class EnemyView:
    def __init__(self, enemy_type):

        base = os.path.join(BASE_PATH, "assets", "images", "enemies", "trolls", enemy_type)

        self.walk = SpriteLoader.load_animation(base + "/walk")
        self.attack = SpriteLoader.load_animation(base + "/attack")
        self.hit = SpriteLoader.load_animation(base + "/hurt")
        self.die = SpriteLoader.load_animation(base + "/die")

        self.frame_index = 0

    def draw(self, screen, enemy):
        frames = self.walk
        image = frames[self.frame_index]

        screen.blit(image, (enemy.x, enemy.y))

        self.frame_index = (self.frame_index + 1) % len(frames)