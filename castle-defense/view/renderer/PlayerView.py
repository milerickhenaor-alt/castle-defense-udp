import os
import pygame
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
            folder = "Warrior"
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

        # 🔥 ESTADO ACTUAL
        self.frame_index = 0
        self.image = None

        # 🔥 VELOCIDAD DE ANIMACIÓN
        self.animation_speed = 0.2

    # ------------------------------------------------------------------
    # 🔥 UPDATE (YA NO RECIBE player)
    # ------------------------------------------------------------------
    def update(self):
        animation = self.walk if self.walk else self.idle

        if animation:
            self.frame_index = (self.frame_index + self.animation_speed) % len(animation)
            self.image = animation[int(self.frame_index)]

    # ------------------------------------------------------------------
    # 🔥 DRAW (USA DATOS DEL MODEL)
    # ------------------------------------------------------------------
    def draw(self, screen, x, y, team):

        if not self.image:
            return

        image = self.image

        # 🔥 VOLTEAR SEGÚN EQUIPO
        if team == "B":
            image = pygame.transform.flip(image, True, False)

        # 🔥 ESCALAR PERSONAJE
        image = pygame.transform.scale(image, (80, 80))

        # 🔥 POSICIONAR
        rect = image.get_rect(center=(x, y))
        screen.blit(image, rect)