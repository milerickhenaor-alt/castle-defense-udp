"""
view/renderer/EnemyView.py

Principios SOLID aplicados
--------------------------
SRP : EnemyView solo carga y dibuja el sprite del enemigo con su barra de vida.
      No conoce la lógica de movimiento ni la red.
LSP : Implementa IDrawable. El Renderer lo trata igual que PlayerView o CastleView.
ISP : Solo implementa update() y draw() — los métodos que realmente necesita.
"""

import os
import pygame
from view.renderer.SpriteLoader import SpriteLoader
from view.renderer.IDrawable import IDrawable

BASE_PATH = os.getcwd()


class EnemyView(IDrawable):
    """
    Vista del enemigo (Troll) — carga animaciones y dibuja sprite + barra de vida.
    Implementa IDrawable (LSP + ISP).
    """

    def __init__(self, enemy, enemy_type):
        self.enemy_type = enemy_type

        # EXTRAER SOLO EL NÚMERO (Ej: "Troll 1" → "1")
        number = str(enemy_type).split(" ")[-1]

        self.base_path = os.path.join(
            BASE_PATH, "assets", "images", "enemies", "trolls", number
        )

        # CARGA DE ANIMACIONES
        try:
            self.walk_frames = SpriteLoader.load_animation(
                os.path.join(self.base_path, "walk")
            )
            self.attack_frames = SpriteLoader.load_animation(
                os.path.join(self.base_path, "attack")
            )
        except Exception as e:
            print(f"❌ Error cargando animaciones: {e}")
            self.walk_frames = []
            self.attack_frames = []

        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = None

    # ------------------------------------------------------------------ #
    #  IDrawable                                                           #
    # ------------------------------------------------------------------ #

    def update(self, enemy=None, *args, **kwargs) -> None:
        """
        [IDrawable] Actualiza el frame de animación según el estado del enemigo.
        SRP: solo actualiza la animación, no mueve al enemigo.
        """
        frames = self.attack_frames if (enemy and enemy.state == "attacking") else self.walk_frames

        if frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(frames):
                self.frame_index = 0
            self.image = frames[int(self.frame_index)]
        else:
            self.image = None

    def draw(self, screen: pygame.Surface, enemy=None, *args, **kwargs) -> None:
        """
        [IDrawable] Dibuja el sprite del enemigo y su barra de vida.
        SRP: solo dibuja, no modifica el estado del enemigo.
        """
        if not enemy:
            return

        if not self.image:
            pygame.draw.rect(screen, (255, 0, 0), (enemy.x - 20, enemy.y - 20, 40, 40))
        else:
            img = self.image
            if enemy.team == "B":
                img = pygame.transform.flip(img, True, False)

            img = pygame.transform.scale(img, (70, 70))
            rect = img.get_rect(center=(int(enemy.x), int(enemy.y)))
            screen.blit(img, rect)

        self._draw_health_bar(screen, enemy)

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _draw_health_bar(self, screen: pygame.Surface, enemy) -> None:
        """
        SRP: método privado separado para dibujar solo la barra de vida.
        Extraído de draw() para mantener cada método con una responsabilidad.
        """
        BAR_WIDTH  = 40
        BAR_HEIGHT = 5
        OFFSET_Y   = 35

        health_ratio = max(0, min(1, enemy.hp / enemy.max_hp))

        bar_x = int(enemy.x - (BAR_WIDTH / 2))
        bar_y = int(enemy.y - OFFSET_Y)

        # Fondo
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT))

        # Vida actual
        current_width = int(BAR_WIDTH * health_ratio)
        color = (0, 255, 0) if health_ratio > 0.3 else (255, 0, 0)
        if current_width > 0:
            pygame.draw.rect(screen, color, (bar_x, bar_y, current_width, BAR_HEIGHT))

        # Borde
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT), 1)