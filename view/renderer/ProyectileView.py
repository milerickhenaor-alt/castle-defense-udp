import pygame
import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class ProjectileView:
    def __init__(self):
        # Ruta que proporcionaste
        self.path = os.path.join(BASE_PATH, "assets", "images", "proyectile", "arrow.png")
        
        try:
            self.image = pygame.image.load(self.path).convert_alpha()
            # Ajustamos el tamaño a algo adecuado (ej: 40x15)
            self.image = pygame.transform.scale(self.image, (40, 15))
            
            # Imagen para el equipo B (volteada horizontalmente)
            self.image_b = pygame.transform.flip(self.image, True, False)
        except Exception as e:
            print(f"Error cargando imagen de proyectil: {e}")
            # Failsafe: Un rectángulo amarillo si no carga la imagen
            self.image = pygame.Surface((20, 5))
            self.image.fill((255, 255, 0))
            self.image_b = self.image

    def draw(self, screen, x, y, team):
        # Elegir la imagen según el equipo
        img = self.image if team == "A" else self.image_b
        
        # Centrar la imagen en la posición Y para que salga de la mano/centro del player
        rect = img.get_rect(center=(int(x), int(y)))
        screen.blit(img, rect)