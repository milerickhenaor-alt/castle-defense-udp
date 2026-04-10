import pygame
import os

# Buscamos la base del proyecto para las rutas
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class ProjectileView:
    def __init__(self):
        # Intentamos ambas carpetas por si acaso (proyectile vs projectile)
        possible_paths = [
            os.path.join(BASE_PATH, "assets", "images", "proyectile", "arrow.png"),
            os.path.join(BASE_PATH, "assets", "images", "projectile", "arrow.png")
        ]
        
        self.image = None
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    self.image = pygame.image.load(path).convert_alpha()
                    self.image = pygame.transform.scale(self.image, (35, 12))
                    break
                except Exception as e:
                    print(f"Error cargando imagen en {path}: {e}")

        # Si no existe la imagen, creamos un rectángulo amarillo de emergencia
        if self.image is None:
            print("⚠️ No se encontró arrow.png. Usando gráfico de emergencia.")
            self.image = pygame.Surface((20, 5))
            self.image.fill((255, 255, 0))

        # Creamos la versión volteada para el equipo B
        self.image_b = pygame.transform.flip(self.image, True, False)

    def draw(self, screen, x, y, team):
        # Elegir imagen según equipo
        img = self.image if team == "A" else self.image_b
        # Centrar el proyectil en la posición (x, y)
        rect = img.get_rect(center=(int(x), int(y)))
        screen.blit(img, rect)