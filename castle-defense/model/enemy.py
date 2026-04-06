from __future__ import annotations
from dataclasses import dataclass, field
import uuid
from model.interfaces import IDamageable, IMovable, ISerializable

@dataclass
class Enemy(IDamageable, IMovable, ISerializable):
    """
    Troll — enemigo autónomo que avanza hacia el castillo contrario.
    """

    team: str
    x: float
    y: float
    hp: int          = 100
    max_hp: int      = 100
    speed: float     = 0.3
    damage: int      = 50
    active: bool     = True
    reward: int      = 10
    width: float     = 45
    height: float    = 45
    
    # 🔥 NUEVO: Atributo de estado para controlar la animación (walking, attacking)
    state: str       = "walking" 
    
    id: str          = field(default_factory=lambda: str(uuid.uuid4()))

    # ------------------------------------------------------------------ #
    #  IMovable — avance automático cada frame                            #
    # ------------------------------------------------------------------ #

    def update(self) -> None:
        """
        [IMovable] Mueve el troll en línea recta.
        Nota: GameState detendrá este movimiento cuando llegue al castillo.
        """
        if self.state == "walking": # Solo se mueve si está caminando
            if self.team == "A":
                self.x += self.speed
            else:
                self.x -= self.speed

    # ------------------------------------------------------------------ #
    #  IDamageable — recibir daño y morir                                 #
    # ------------------------------------------------------------------ #

    def take_damage(self, amount: int) -> bool:
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.active = False
            return True
        return False

    @property
    def is_alive(self) -> bool:
        return self.active and self.hp > 0

    @property
    def hp_ratio(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    # ------------------------------------------------------------------ #
    #  Colisión con castillo                                               #
    # ------------------------------------------------------------------ #

    def has_reached_castle(self, castle_x: float, castle_width: float) -> bool:
        """
        Determina si el troll está lo suficientemente cerca para golpear.
        """
        margen_ataque = 5 # Pixeles de distancia para empezar a golpear
        if self.team == "A":
            return (self.x + self.width) >= (castle_x - margen_ataque)
        else:
            return self.x <= (castle_x + castle_width + margen_ataque)

    # ------------------------------------------------------------------ #
    #  ISerializable — sincronización UDP                                 #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        """Agregamos 'state' al diccionario para que la red lo sincronice."""
        return {
            "id":      self.id,
            "team":    self.team,
            "x":       self.x,
            "y":       self.y,
            "hp":      self.hp,
            "max_hp":  self.max_hp,
            "speed":   self.speed,
            "damage":  self.damage,
            "active":  self.active,
            "reward":  self.reward,
            "state":   self.state, # 🔥 Sincronizar estado
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Enemy":
        e = cls(
            team=data["team"],
            x=data["x"],
            y=data["y"],
            hp=data.get("hp", 100),
            max_hp=data.get("max_hp", 100),
            speed=data.get("speed", 0.5),
            damage=data.get("damage", 50),
            active=data.get("active", True),
            reward=data.get("reward", 10),
            state=data.get("state", "walking"), # 🔥 Cargar estado
        )
        e.id = data.get("id", e.id)
        return e