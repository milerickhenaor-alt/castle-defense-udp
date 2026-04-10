"""
view/renderer/CastleView.py

Principios SOLID aplicados
--------------------------
SRP : CastleView solo carga y dibuja el sprite del castillo según su estado de vida.
      No conoce la lógica del juego ni la red.
LSP : Implementa IDrawable. El Renderer lo trata igual que PlayerView o EnemyView.
ISP : Solo implementa update() y draw() — los métodos que realmente necesita.
OCP : Si se agrega un nuevo estado del castillo (ej: "burning"), solo se agrega
      una imagen y una condición en draw(). No se modifica el Renderer.
"""

import os
import pygame
from view.renderer.IDrawable import IDrawable

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class CastleView(IDrawable):
    """
    Vista del castillo — carga imágenes por estado y dibuja según HP.
    Implementa IDrawable (LSP + ISP).
    """

    def __init__(self, castle_data):
        variant = str(castle_data["variant"])

        base = os.path.join(
            BASE_PATH,
            "assets",
            "images",
            "castles",
            f"castle{variant}"
        )

        self.full      = self._load_image(base, "full.png")
        self.damaged   = self._load_image(base, "damaged.png")
        self.destroyed = self._load_image(base, "destroyed.png")

    # ------------------------------------------------------------------ #
    #  IDrawable                                                           #
    # ------------------------------------------------------------------ #

    def update(self, *args, **kwargs) -> None:
        """
        [IDrawable] El castillo no tiene animación propia.
        Se implementa para cumplir el contrato de IDrawable (LSP).
        """
        pass

    def draw(self, screen: pygame.Surface, castle=None, *args, **kwargs) -> None:
        """
        [IDrawable] Dibuja el castillo según su HP actual.
        OCP: agregar un nuevo estado no requiere modificar el Renderer.
        SRP: solo dibuja, no modifica el estado del castillo.
        """
        if not castle:
            return

        if castle.hp > 130:
            image = self.full
        elif castle.hp > 75:
            image = self.damaged
        else:
            image = self.destroyed

        if image:
            img = pygame.transform.scale(image, (230, 230))

            if castle.team == "A":
                img = pygame.transform.flip(img, True, False)

            screen.blit(img, (castle.x, castle.y))

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _load_image(self, base: str, filename: str):
        """
        SRP: método privado para cargar una imagen con manejo de errores.
        Separado de __init__ para mantener responsabilidades claras.
        """
        path = os.path.join(base, filename)
        if not os.path.exists(path):
            print(f"⚠️ No existe: {path}")
            return None
        return pygame.image.load(path).convert_alpha()