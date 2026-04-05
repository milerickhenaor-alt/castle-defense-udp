"""
model/interfaces.py
Persona 1 — Model Core

Define las interfaces (clases base abstractas) del modelo.

¿Por qué están aquí?
--------------------
Principio ISP (Interface Segregation):
    En vez de una sola clase base gigante con todos los métodos posibles,
    se definen interfaces pequeñas y específicas. Cada clase concreta
    implementa solo las interfaces que necesita.

    Por ejemplo:
        - IDamageable  → cualquier cosa que pueda recibir daño (castillo, enemigo)
        - IMovable     → cualquier cosa que se mueva (jugador, enemigo, proyectil)
        - ISerializable → cualquier cosa que viaje por la red

Principio LSP (Liskov Substitution):
    Cualquier subclase puede usarse donde se espera la clase base sin romper
    el comportamiento. Por ejemplo, el sistema de colisiones solo necesita
    saber que algo es IDamageable; no le importa si es Castle o Enemy.
"""

from abc import ABC, abstractmethod


# ─────────────────────────────────────────────────────────────────────────────
# ISP — interfaces pequeñas y específicas
# ─────────────────────────────────────────────────────────────────────────────

class IDamageable(ABC):
    """
    [ISP] Interfaz para entidades que pueden recibir daño.
    La implementan: Enemy, Castle.
    NO la implementa Player (los jugadores no tienen vida en este juego).
    """

    @abstractmethod
    def take_damage(self, amount: int) -> bool:
        """
        Aplica `amount` puntos de daño.
        Devuelve True si la entidad fue destruida/eliminada en este golpe.
        """
        ...

    @property
    @abstractmethod
    def is_alive(self) -> bool:
        """True mientras la entidad siga activa."""
        ...

    @property
    @abstractmethod
    def hp_ratio(self) -> float:
        """Fracción de vida restante [0.0 – 1.0]. Usada por el HUD (Persona 2)."""
        ...


class IMovable(ABC):
    """
    [ISP] Interfaz para entidades que se desplazan cada frame.
    La implementan: Enemy, Projectile.
    Player tiene su propia lógica de movimiento basada en input.
    """

    @abstractmethod
    def update(self) -> None:
        """Avanza la entidad un frame según su lógica interna."""
        ...


class ISerializable(ABC):
    """
    [ISP] Interfaz para entidades que viajan por la red (UDP).
    La implementan: Player, Enemy, Castle, Projectile.

    ¿Por qué separarla?
    Porque no toda entidad necesita serializarse (ej: objetos de UI),
    y no toda entidad serializable necesita moverse o recibir daño.
    """

    @abstractmethod
    def to_dict(self) -> dict:
        """Convierte el estado a un dict serializable en JSON."""
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "ISerializable":
        """Reconstruye la entidad desde un dict recibido por red."""
        ...