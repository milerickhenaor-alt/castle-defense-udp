import os
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class PlayerView:
    def __init__(self, player_data):

        # player_data = { "type": "Fairies", "variant": "2" }

        base = os.path.join(
            BASE_PATH,
            "assets",
            "images",
            "players",
            player_data["type"],
            player_data["variant"]
        )

        self.walk = SpriteLoader.load_animation(os.path.join(base, "walk"))
        self.attack = SpriteLoader.load_animation(os.path.join(base, "attack"))
    
        self.frame_index = 0

    def draw(self, screen, player):

        frames = self.walk
        image = frames[self.frame_index]

        screen.blit(image, (player.x, player.y))

        self.frame_index = (self.frame_index + 1) % len(frames)