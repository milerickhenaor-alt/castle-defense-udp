import os
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class PlayerView:
    def __init__(self, player_data):

        # 🔥 SOPORTA STRING O DICT
        if isinstance(player_data, dict):
            player_name = player_data.get("name", "Fairy 1")
        else:
            player_name = player_data

        self.player_name = player_name

        # 🔥 EXTRAER TIPO Y NÚMERO
        parts = player_name.split(" ")
        tipo = parts[0]
        numero = parts[1]

        # 🔥 MAPEAR CARPETAS CORRECTAS
        if tipo == "Fairy":
            folder = "Fairies"
        elif tipo == "Gent":
            folder = "Gentlemen"
        elif tipo == "War":
            folder = "Warriors"
        else:
            folder = tipo

        # 🔥 RUTA BASE
        base = os.path.join(
            BASE_PATH,
            "assets",
            "images",
            "players",
            folder,
            numero
        )

        # 🔥 CARGAR ANIMACIONES
        self.walk = SpriteLoader.load_animation(os.path.join(base, "walk"))
        self.idle = SpriteLoader.load_animation(os.path.join(base, "idle"))

        self.frame_index = 0
        self.image = self.idle[0] if self.idle else None

    def update(self):
        if self.walk:
            self.frame_index = (self.frame_index + 0.2) % len(self.walk)
            self.image = self.walk[int(self.frame_index)]

    def draw(self, screen, x, y):
        if self.image:
            rect = self.image.get_rect(center=(x, y))
            screen.blit(self.image, rect)