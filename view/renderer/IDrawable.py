"""
view/renderer/IDrawable.py

Interfaz IDrawable — Principios SOLID aplicados
------------------------------------------------

ISP (Interface Segregation Principle):
    En vez de una clase base gigante con todos los métodos posibles,
    IDrawable define solo los métodos que cualquier entidad visual
    necesita: update() y draw(). Nada más.

LSP (Liskov Substitution Principle):
    PlayerView, EnemyView y CastleView implementan IDrawable.
    El Renderer puede tratarlos a todos como IDrawable sin conocer
    sus detalles internos. Si mañana se agrega ProjectileView,
    solo necesita implementar IDrawable y el Renderer lo acepta.

OCP (Open/Closed Principle):
    El Renderer está abierto para extensión (nuevos views) pero
    cerrado para modificación. No hay que tocarlo para agregar
    un nuevo tipo de entidad visual.
"""

from abc import ABC, abstractmethod
import pygame


class IDrawable(ABC):
    """
    Interfaz base para todas las vistas de entidades del juego.
    Cualquier clase que quiera ser renderizada debe implementarla.
    """

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """
        Actualiza el estado interno de la vista (animación, frame, etc).
        Se llama cada frame antes de draw().
        """
        ...

    @abstractmethod
    def draw(self, screen: pygame.Surface, *args, **kwargs) -> None:
        """
        Dibuja la entidad en la pantalla.
        SRP: solo dibuja, no actualiza lógica del juego.
        """
        ...