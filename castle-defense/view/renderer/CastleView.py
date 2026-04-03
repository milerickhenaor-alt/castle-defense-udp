import os
import pygame
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class CastleView:
    def __init__(self, castle_type):

        base = os.path.join(BASE_PATH, "assets", "images", "castles", f"castle{castle_type}")

        self.full =  [pygame.image.load(base + "/full.png")]
        self.damaged = [pygame.image.load(base + "/damaged.png")]
        self.destroyed =[pygame.image.load(base + "/destroyed.png")] 

        self.frame_index = 0
        self.state = "full"

    def draw(self, screen, castle):

        if self.state == "full":
            frames = self.full
        elif self.state == "damaged":
            frames = self.damaged
        else:
            frames = self.destroyed

        image = frames[self.frame_index]
        screen.blit(image, (castle.x, castle.y))

        self.frame_index = (self.frame_index + 1) % len(frames)