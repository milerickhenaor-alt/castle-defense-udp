"""
model/castle.py
Persona 1 — Model Core

Clase Castle: castillo de cada equipo.

Principios SOLID aplicados
--------------------------
SRP : Castle solo gestiona su vida y estado de destrucción.
ISP : Implementa IDamageable e ISerializable.
      NO implementa IMovable porque los castillos no se mueven.
      Esto demuestra ISP: las interfaces son pequeñas y opcionales.
LSP : Castle puede usarse donde se espere IDamageable junto a Enemy,
      y el sistema de colisiones funciona igual para ambos.
      Diferencia de contrato: take_damage en Castle siempre devuelve
      False (un castillo no "muere" como un Enemy; su destrucción se
      detecta por is_destroyed), lo que está documentado explícitamente
      para no violar LSP implícitamente.
"""

from __future__ import annotations

from dataclasses import dataclass

from model.interfaces import IDamageable, ISerializable


@dataclass
class Castle(IDamageable, ISerializable):
    """
    Castillo de un equipo.

    Atributos
    ---------
    team     : 'A' | 'B'
    x, y     : posición (esquina superior izquierda)
    hp       : vida actual
    max_hp   : vida máxima (por defecto 1000)
    width    : ancho en píxeles
    height   : alto en píxeles
    """

    team: str
    x: float
    y: float
    max_hp: int   = 1000
    hp: int       = 1000
    width: float  = 64.0
    height: float = 128.0

    # ------------------------------------------------------------------ #
    #  IDamageable                                                         #
    # ------------------------------------------------------------------ #

    def take_damage(self, amount: int) -> bool:
        """
        [IDamageable] Reduce la vida del castillo.

        Nota de contrato (LSP):
            A diferencia de Enemy.take_damage(), este método siempre
            devuelve False. La destrucción del castillo se detecta mediante
            la propiedad is_destroyed, no por el valor de retorno.
            Esto está documentado para evitar que los consumidores de
            IDamageable asuman el mismo comportamiento que Enemy.
        """
        self.hp = max(0, self.hp - amount)
        return False  # Ver nota de contrato arriba

    @property
    def is_alive(self) -> bool:
        """[IDamageable] True mientras el castillo no haya sido destruido."""
        return self.hp > 0

    @property
    def is_destroyed(self) -> bool:
        """True cuando el castillo ha caído. Dispara el fin del juego."""
        return self.hp <= 0

    @property
    def hp_ratio(self) -> float:
        """[IDamageable] Fracción de vida [0.0–1.0]. Usada por el HUD."""
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    # ------------------------------------------------------------------ #
    #  ISerializable                                                       #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        """[ISerializable] Convierte el estado a dict para enviarlo por UDP."""
        return {
            "team":   self.team,
            "x":      self.x,
            "y":      self.y,
            "hp":     self.hp,
            "max_hp": self.max_hp,
            "width":  self.width,
            "height": self.height,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Castle":
        """[ISerializable] Reconstruye un Castle desde un dict recibido por red."""
        return cls(
            team=data["team"],
            x=data["x"],
            y=data["y"],
            max_hp=data.get("max_hp", 1000),
            hp=data.get("hp", 1000),
            width=data.get("width", 64.0),
            height=data.get("height", 128.0),
        )

    def __repr__(self) -> str:
        return f"Castle(team={self.team!r}, hp={self.hp}/{self.max_hp})"