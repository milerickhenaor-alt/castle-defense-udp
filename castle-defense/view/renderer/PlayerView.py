import os
import pygame
from view.renderer.SpriteLoader import SpriteLoader

# Buscamos la raíz del proyecto para las rutas de assets
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class PlayerView:
    def __init__(self, player_data):
        """
        Soporta:
        - Objeto Player (tiene atributo .name)
        - Diccionario (tiene clave "name")
        - String directo (ej: "Fairy 1")
        """
        # 1. EXTRAER EL NOMBRE SEGÚN EL TIPO DE DATO RECIBIDO
        if hasattr(player_data, "name"):
            # Si es el objeto Player del modelo
            player_name = player_data.name
        elif isinstance(player_data, dict):
            # Si es un diccionario de selección
            player_name = player_data.get("name", "Fairy 1")
        else:
            # Si es un string directo
            player_name = str(player_data)

        self.player_name = player_name

        # 2. EXTRAER TIPO Y NÚMERO (Ej: "Fairy 1" -> ["Fairy", "1"])
        try:
            parts = player_name.split(" ")
            tipo = parts[0]
            numero = parts[1]
        except (IndexError, AttributeError):
            # Fallback en caso de nombre mal formateado
            tipo = "Fairy"
            numero = "1"

        # 3. MAPEAR CARPETAS CORRECTAS SEGÚN TU ESTRUCTURA DE ASSETS
        if tipo == "Fairy":
            folder = "Fairies"
        elif tipo == "Gent":
            folder = "Gentlemen"
        elif tipo == "War":
            folder = "Warrior"
        else:
            folder = tipo

        # 4. CONSTRUIR RUTA BASE
        # assets/images/players/Fairies/1/
        base = os.path.join(
            BASE_PATH,
            "assets",
            "images",
            "players",
            folder,
            numero
        )

        # 5. CARGAR ANIMACIONES USANDO EL SPRITELOADER
        self.walk = SpriteLoader.load_animation(os.path.join(base, "walk"))
        self.idle = SpriteLoader.load_animation(os.path.join(base, "idle"))

        # 6. ESTADO DE LA ANIMACIÓN
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = None

    def update(self):
        """
        Actualiza el frame de la animación. 
        Prioriza caminar, si no hay frames de caminar usa idle.
        """
        animation = self.walk if self.walk else self.idle

        if animation and len(animation) > 0:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                self.frame_index = 0
            self.image = animation[int(self.frame_index)]

    def draw(self, screen, x, y, team):
        """
        Dibuja el sprite en pantalla.
        - team: 'A' o 'B' para voltear el sprite.
        - x, y: coordenadas que vienen del modelo.
        """
        if not self.image:
            return

        # Copiamos la imagen actual para no alterar la original al transformar
        image_to_draw = self.image

        # VOLTEAR SEGÚN EQUIPO (Equipo B mira hacia la izquierda)
        if team == "B":
            image_to_draw = pygame.transform.flip(image_to_draw, True, False)

        # ESCALAR PERSONAJE (Ajustado a 80x80 para que quepa bien en el carril)
        image_to_draw = pygame.transform.scale(image_to_draw, (80, 80))

        # POSICIONAR CENTRADO EN LAS COORDENADAS
        rect = image_to_draw.get_rect(center=(int(x), int(y)))
        screen.blit(image_to_draw, rect)