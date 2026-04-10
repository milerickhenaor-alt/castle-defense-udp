"""
model/projectile.py
Persona 1 — Model Core

Clase Projectile: proyectil disparado por un jugador.

Principios SOLID aplicados
--------------------------
SRP : Projectile solo gestiona su vuelo y colisión como punto geométrico.
      No sabe cómo se dibuja (Persona 2) ni cómo se envía por red (Persona 4).
ISP : Implementa IMovable (se actualiza cada frame) e ISerializable (viaja por UDP).
      NO implementa IDamageable porque un proyectil no recibe daño.
LSP : Puede usarse donde se espere IMovable junto a Enemy.
      El game loop llama a update() sobre ambos de la misma forma.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import uuid

from model.interfaces import IMovable, ISerializable


@dataclass
class Projectile(IMovable, ISerializable):
    """
    Proyectil en vuelo.

    Atributos
    ---------
    owner_name : nombre del jugador que lo disparó (para asignar puntos)
    team       : equipo del dueño ('A' | 'B')
    x, y       : posición actual
    dx, dy     : componentes de dirección (normalizados)
    speed      : píxeles por frame
    damage     : daño que produce al impactar
    active     : False → debe eliminarse del estado del juego
    id         : UUID único para sincronización entre PCs
    """

    owner_name: str
    team: str
    x: float
    y: float
    dx: float
    dy: float
    speed: float  = 10.0
    damage: int   = 25
    active: bool  = True
    id: str       = field(default_factory=lambda: str(uuid.uuid4()))

    # ------------------------------------------------------------------ #
    #  IMovable                                                            #
    # ------------------------------------------------------------------ #

    def update(self) -> None:
        """
        [IMovable] Avanza el proyectil un frame según su dirección y velocidad.

        LSP: el game loop puede llamar update() sobre una lista mixta de
        IMovable (Enemy + Projectile) sin distinguir tipos.
        """
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    # ------------------------------------------------------------------ #
    #  Estado y colisión                                                   #
    # ------------------------------------------------------------------ #

    def is_out_of_bounds(self, map_width: int, map_height: int) -> bool:
        """True si el proyectil salió de los límites del mapa."""
        return (
            self.x < 0 or self.x > map_width or
            self.y < 0 or self.y > map_height
        )

    def deactivate(self) -> None:
        """
        Marca el proyectil como inactivo.
        El GameState lo eliminará en el siguiente ciclo de limpieza.
        """
        self.active = False

    def collides_with(
        self,
        target_x: float,
        target_y: float,
        target_w: float,
        target_h: float,
    ) -> bool:
        """
        Colisión AABB (Axis-Aligned Bounding Box).
        El proyectil se trata como un punto; el objetivo como un rectángulo.

        La lógica visual/sprite queda en el renderer de Persona 2;
        aquí solo hay matemática pura (SRP).
        """
        return (
            target_x <= self.x <= target_x + target_w and
            target_y <= self.y <= target_y + target_h
        )

    # ------------------------------------------------------------------ #
    #  ISerializable                                                       #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        """[ISerializable] Convierte el estado a dict para enviarlo por UDP."""
        return {
            "id":         self.id,
            "owner_name": self.owner_name,
            "team":       self.team,
            "x":          self.x,
            "y":          self.y,
            "dx":         self.dx,
            "dy":         self.dy,
            "speed":      self.speed,
            "damage":     self.damage,
            "active":     self.active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Projectile":
        """[ISerializable] Reconstruye un Projectile desde un dict recibido por red."""
        p = cls(
            owner_name=data["owner_name"],
            team=data["team"],
            x=data["x"],
            y=data["y"],
            dx=data["dx"],
            dy=data["dy"],
            speed=data.get("speed", 10.0),
            damage=data.get("damage", 25),
            active=data.get("active", True),
        )
        p.id = data.get("id", p.id)
        return p