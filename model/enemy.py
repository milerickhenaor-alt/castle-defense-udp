from __future__ import annotations
from dataclasses import dataclass, field
import uuid
from model.interfaces import IDamageable, IMovable, ISerializable

@dataclass
class Enemy(IDamageable, IMovable, ISerializable):
    """
    Troll — enemigo autónomo que avanza hacia el castillo contrario.
    """

    # --- Campos Obligatorios ---
    team: str
    x: float
    y: float
    
    # --- Configuración ---
    type: str        = "Troll 1"
    hp: int          = 100
    max_hp: int      = 100
    speed: float     = 0.3
    damage: int      = 50
    active: bool     = True
    reward: int      = 10
    width: float     = 45
    height: float    = 45
    state: str       = "walking"

    # ID único (sincronización)
    id: str          = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # ------------------------------------------------------------------ #
    #  POST INIT (🔥 CLAVE: asegurar tipos correctos)
    # ------------------------------------------------------------------ #

    def __post_init__(self):
        """
        Garantiza que x e y siempre sean float (evita errores de red).
        """
        try:
            self.x = float(self.x)
            self.y = float(self.y)
        except (ValueError, TypeError):
            print(f"⚠️ Error convirtiendo posición Enemy: x={self.x}, y={self.y}")
            self.x = 0.0
            self.y = 0.0

    # ------------------------------------------------------------------ #
    #  MOVIMIENTO
    # ------------------------------------------------------------------ #

    def update(self) -> None:
        if self.state == "walking" and self.active:
            if self.team == "A":
                self.x += self.speed
            else:
                self.x -= self.speed

    # ------------------------------------------------------------------ #
    #  DAÑO
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
    #  SERIALIZACIÓN
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "id":       self.id,
            "team":     self.team,
            "type":     self.type,
            "x":        float(self.x),
            "y":        float(self.y),
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
        """
        🔥 Método correcto para reconstruir enemigos desde red
        """

        enemy = cls(
            team=data["team"],
            x=float(data["x"]),  # 🔥 SIEMPRE float
            y=float(data["y"]),
            type=data.get("type", "Troll 1"),
            hp=int(data.get("hp", 100)),
            max_hp=int(data.get("max_hp", 100)),
            speed=float(data.get("speed", 0.3)),
            damage=int(data.get("damage", 50)),
            active=bool(data.get("active", True)),
            reward=int(data.get("reward", 10)),
            state=data.get("state", "walking"),
        )

        # 🔥 Mantener ID del servidor
        if "id" in data:
            enemy.id = data["id"]

        return enemy
