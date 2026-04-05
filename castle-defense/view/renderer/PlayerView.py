import os
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class PlayerView:
    def __init__(self, player_data):

        player_type = player_data["type"]
        variant = str(player_data["variant"])  # 🔥 FIX

        base = os.path.join(
            BASE_PATH,
            "assets",
            "images",
            "players",
            player_type,
            variant
        )

        self.walk = SpriteLoader.load_animation(os.path.join(base, "walk"))
        self.attack = SpriteLoader.load_animation(os.path.join(base, "attack"))

        self.frame_index = 0

    def draw(self, screen, player):
        if not self.walk:
            return

        image = self.walk[self.frame_index % len(self.walk)]
        screen.blit(image, (player.x, player.y))

        self.frame_index += 1