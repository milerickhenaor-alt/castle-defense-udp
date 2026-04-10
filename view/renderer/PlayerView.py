import os
import pygame
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class PlayerView:
    def __init__(self, player_data):
        # 1. Extraer el nombre (puede venir objeto, dict o string)
        if hasattr(player_data, "name"):
            player_name = player_data.name
        elif isinstance(player_data, dict):
            player_name = player_data.get("name", "Fairy 1")
        else:
            player_name = str(player_data)

        self.player_name = player_name

        # 2. Parsear "Tipo" y "Número" (Ej: "War 1" -> "War", "1")
        try:
            parts = player_name.split(" ")
            tipo = parts[0]
            numero = parts[1]
        except:
            tipo, numero = "Fairy", "1"

        # 3. Mapear a carpetas reales
        mapping = {
            "Fairy": "Fairies",
            "Gent": "Gentlemen",
            "War": "Warrior"
        }
        folder = mapping.get(tipo, tipo)

        # 4. Construir ruta y cargar sprites
        base = os.path.join(BASE_PATH, "assets", "images", "players", folder, numero)
        
        self.walk = SpriteLoader.load_animation(os.path.join(base, "walk"))
        self.idle = SpriteLoader.load_animation(os.path.join(base, "idle"))

        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = None

    def update(self):
        # Priorizar caminar, si no hay frames usa idle
        animation = self.walk if self.walk else self.idle
        if animation:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                self.frame_index = 0
            self.image = animation[int(self.frame_index)]

    def draw(self, screen, x, y, team):
        if not self.image:
            # Cuadro azul de debug si no hay imagen
            pygame.draw.rect(screen, (0, 0, 255), (x-20, y-20, 40, 40))
            return

        image_to_draw = self.image
        if team == "B":
            image_to_draw = pygame.transform.flip(image_to_draw, True, False)

        image_to_draw = pygame.transform.scale(image_to_draw, (80, 80))
        rect = image_to_draw.get_rect(center=(int(x), int(y)))
        screen.blit(image_to_draw, rect)