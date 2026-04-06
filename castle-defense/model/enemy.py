from __future__ import annotations
from dataclasses import dataclass, field
import uuid
from model.interfaces import IDamageable, IMovable, ISerializable

@dataclass
class Enemy(IDamageable, IMovable, ISerializable):
    """
    Troll — enemigo autónomo que avanza hacia el castillo contrario.
    """
    # --- Campos Obligatorios (Sin default) ---
    team: str
    x: float
    y: float
    
    # --- Campos con Default ---
    # 🔥 Agregamos 'type' para que la Factory pueda pasarlo sin error
    type: str        = "Troll 1" 
    hp: int          = 100
    max_hp: int      = 100
    speed: float     = 0.3
    damage: int      = 50
    active: bool     = True
    reward: int      = 10
    width: float     = 45
    height: float    = 45
    
    # Atributo de estado para controlar la animación (walking, attacking)
    state: str       = "walking" 
    
    # ID único para sincronización
    id: str          = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # ------------------------------------------------------------------ #
    #  IMovable — avance automático cada frame                            #
    # ------------------------------------------------------------------ #

    def update(self) -> None:
        """
        Mueve el troll en línea recta si su estado es 'walking'.
        """
        if self.state == "walking" and self.active:
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
    #  ISerializable — sincronización UDP                                 #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "id":       self.id,
            "team":     self.team,
            "type":     self.type,   # 🔥 Sincronizar el tipo de Troll
            "x":        self.x,
            "y":        self.y,
            "hp":       self.hp,
            "max_hp":   self.max_hp,
            "speed":    self.speed,
            "damage":   self.damage,
            "active":   self.active,
            "reward":   self.reward,
            "state":    self.state,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Enemy":
        # Extraemos el ID aparte porque no se pasa en el constructor de la dataclass 
        # si queremos que se asigne el del diccionario.
        e = cls(
            team=data["team"],
            x=data["x"],
            y=data["y"],
            type=data.get("type", "Troll 1"),
            hp=data.get("hp", 100),
            max_hp=data.get("max_hp", 100),
            speed=data.get("speed", 0.5),
            damage=data.get("damage", 50),
            active=data.get("active", True),
            reward=data.get("reward", 10),
            state=data.get("state", "walking"),
        )
        if "id" in data:
            e.id = data["id"]
        return e