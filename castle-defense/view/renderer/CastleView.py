import os
import pygame

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class CastleView:
    def __init__(self, castle_data):

        variant = str(castle_data["variant"])  # 🔥 FIX

        base = os.path.join(
            BASE_PATH,
            "assets",
            "images",
            "castles",
            f"castle{variant}"
        )

        self.full = self.load_image(base, "full.png")
        self.damaged = self.load_image(base, "damaged.png")
        self.destroyed = self.load_image(base, "destroyed.png")

    def load_image(self, base, filename):
        path = os.path.join(base, filename)

        if not os.path.exists(path):
            print(f"⚠️ No existe: {path}")
            return None

        return pygame.image.load(path).convert_alpha()

    def draw(self, screen, castle):

        # 🔥 USAR VIDA REAL (NO self.state)
        if castle.health > 130:
            image = self.full
        elif castle.health > 60:
            image = self.damaged
        else:
            image = self.destroyed

        if image:
            screen.blit(image, (castle.x, castle.y))