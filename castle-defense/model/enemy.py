"""
model/enemy.py
Persona 1 — Model Core

Clase Enemy (Troll): enemigo autónomo generado desde cada castillo.

Principios SOLID aplicados
--------------------------
SRP : Enemy solo gestiona su propio estado (movimiento, vida, daño).
      No sabe cómo se dibuja ni cómo se envía por red.
ISP : Implementa las tres interfaces que realmente necesita:
        - IMovable     → se mueve cada frame (update)
        - IDamageable  → puede recibir daño (take_damage)
        - ISerializable → su estado viaja por UDP
      Si se agrega un objeto del juego que no se mueva, no tendría
      que implementar IMovable. Eso es ISP.
LSP : Enemy puede usarse donde se espere IDamageable o IMovable
      sin cambiar el comportamiento esperado. El sistema de colisiones,
      por ejemplo, solo necesita IDamageable y funciona igual con
      cualquier subclase futura de Enemy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import uuid

from model.interfaces import IDamageable, IMovable, ISerializable


@dataclass
class Enemy(IDamageable, IMovable, ISerializable):
    """
    Troll — enemigo autónomo que avanza hacia el castillo contrario.

    Atributos
    ---------
    team     : equipo al que pertenece ('A' | 'B')
    x, y     : posición actual
    hp       : vida actual
    max_hp   : vida máxima
    speed    : píxeles por frame
    damage   : daño que inflige al castillo al llegar
    active   : False → debe eliminarse del juego
    reward   : puntos que otorga al morir
    width/height : dimensiones para detección de colisión
    id       : identificador único (para sincronización UDP)
    """

    team: str
    x: float
    y: float
    hp: int        = 100
    max_hp: int    = 100
    speed: float   = 1.5
    damage: int    = 50
    active: bool   = True
    reward: int    = 10
    width: float   = 32.0
    height: float  = 32.0
    id: str        = field(default_factory=lambda: str(uuid.uuid4()))

    # ------------------------------------------------------------------ #
    #  IMovable — avance automático cada frame                            #
    # ------------------------------------------------------------------ #

    def update(self) -> None:
        """
        [IMovable] Mueve el troll en línea recta hacia el castillo enemigo.

        Regla del juego:
            Equipo A → nace en el castillo izquierdo, avanza hacia la derecha.
            Equipo B → nace en el castillo derecho, avanza hacia la izquierda.
        """
        if self.team == "A":
            self.x += self.speed
        else:
            self.x -= self.speed

    # ------------------------------------------------------------------ #
    #  IDamageable — recibir daño y morir                                 #
    # ------------------------------------------------------------------ #

    def take_damage(self, amount: int) -> bool:
        """
        [IDamageable] Aplica daño al troll.

        LSP: el GameState llama a take_damage() sobre cualquier IDamageable
        (Enemy o Castle) de la misma forma. Esta implementación respeta
        el contrato: devuelve True si la entidad murió.
        """
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.active = False
            return True
        return False

    @property
    def is_alive(self) -> bool:
        """[IDamageable] True mientras el troll esté activo y con vida."""
        return self.active and self.hp > 0

    @property
    def hp_ratio(self) -> float:
        """[IDamageable] Fracción de vida [0.0–1.0]. Usada por el HUD."""
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    # ------------------------------------------------------------------ #
    #  Colisión con castillo                                               #
    # ------------------------------------------------------------------ #

    def has_reached_castle(self, castle_x: float, castle_width: float) -> bool:
        """
        True si el troll llegó al castillo enemigo.
        Equipo A ataca al castillo B (derecha del mapa).
        Equipo B ataca al castillo A (izquierda del mapa).
        """
        if self.team == "A":
            return self.x + self.width >= castle_x
        else:
            return self.x <= castle_x + castle_width

    # ------------------------------------------------------------------ #
    #  ISerializable — sincronización UDP                                 #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        """[ISerializable] Convierte el estado a dict para enviarlo por red."""
        return {
            "id":     self.id,
            "team":   self.team,
            "x":      self.x,
            "y":      self.y,
            "hp":     self.hp,
            "max_hp": self.max_hp,
            "speed":  self.speed,
            "damage": self.damage,
            "active": self.active,
            "reward": self.reward,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Enemy":
        """[ISerializable] Reconstruye un Enemy desde un dict recibido por red."""
        e = cls(
            team=data["team"],
            x=data["x"],
            y=data["y"],
            hp=data.get("hp", 100),
            max_hp=data.get("max_hp", 100),
            speed=data.get("speed", 1.5),
            damage=data.get("damage", 50),
            active=data.get("active", True),
            reward=data.get("reward", 10),
        )
        e.id = data.get("id", e.id)
        return e