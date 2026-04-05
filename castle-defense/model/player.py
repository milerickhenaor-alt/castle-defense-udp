"""
model/player.py
Persona 1 — Model Core

Clase Player: representa un jugador humano.

Principios SOLID aplicados
--------------------------
SRP : Player gestiona solo su estado (posición, nombre, puntaje).
ISP : Implementa IMovable e ISerializable.
      NO implementa IDamageable porque no tiene vida.
LSP : Puede usarse donde se espere IMovable.
"""

from __future__ import annotations
from dataclasses import dataclass

from model.interfaces import IMovable, ISerializable


@dataclass
class Player(IMovable, ISerializable):
    """
    Jugador del juego.

    Atributos
    ---------
    name   : nombre del jugador
    team   : 'A' | 'B'
    x, y   : posición
    score  : puntaje
    speed  : velocidad de movimiento
    width/height : tamaño para colisiones/render
    """

    name: str
    team: str
    x: float
    y: float
    score: int = 0
    speed: float = 5.0
    width: float = 32.0
    height: float = 48.0

    # ───────────────────────────────────────────── #
    # IMovable
    # ───────────────────────────────────────────── #

    def update(self) -> None:
        """
        Movimiento vacío porque el control lo hace el controller.
        Se mantiene para cumplir IMovable (LSP).
        """
        pass

    def move(self, dx: float, dy: float) -> None:
        """
        Movimiento controlado por input (controller).
        """
        self.x += dx * self.speed
        self.y += dy * self.speed

    def set_position(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    # ───────────────────────────────────────────── #
    # Lógica de juego
    # ───────────────────────────────────────────── #

    def add_score(self, amount: int) -> None:
        self.score += amount

    # ───────────────────────────────────────────── #
    # ISerializable (UDP)
    # ───────────────────────────────────────────── #

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "team": self.team,
            "x": self.x,
            "y": self.y,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        return cls(
            name=data["name"],
            team=data["team"],
            x=data["x"],
            y=data["y"],
            score=data.get("score", 0),
        )

    def __repr__(self):
        return f"Player(name={self.name}, team={self.team}, score={self.score})"