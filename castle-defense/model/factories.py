from __future__ import annotations
from model.enemy      import Enemy
from model.projectile import Projectile

class EnemyFactory:
    """
    Crea instancias de Enemy con configuración balanceada.
    """
    # 🔥 VELOCIDADES REDUCIDAS PARA JUGABILIDAD
    _TYPES: dict = {
        "normal": {"hp": 100, "max_hp": 100, "speed": 0.6, "damage": 20, "reward": 10, "width": 32.0, "height": 32.0},
        "fast":   {"hp":  50, "max_hp":  50, "speed": 1.1, "damage": 10, "reward": 15, "width": 24.0, "height": 24.0},
        "tank":   {"hp": 250, "max_hp": 250, "speed": 0.3, "damage": 40, "reward": 30, "width": 48.0, "height": 48.0},
    }

    @classmethod
    def create(cls, team: str, spawn_x: float, spawn_y: float, enemy_type: str = "normal") -> Enemy:
        if enemy_type not in cls._TYPES:
            raise ValueError(f"Tipo desconocido: {enemy_type}")

        params = cls._TYPES[enemy_type]
        return Enemy(
            team=team,
            x=spawn_x,
            y=spawn_y,
            **params,
        )

    @classmethod
    def create_wave(cls, team, spawn_x, spawn_y, wave_number=1):
        enemies = []
        # En cada oleada sale un enemigo base
        enemies.append(cls.create(team, spawn_x, spawn_y, "normal"))

        # Dificultad progresiva
        if wave_number >= 3 and wave_number % 2 == 0:
            enemies.append(cls.create(team, spawn_x, spawn_y + 50, "fast"))
        
        if wave_number >= 5 and wave_number % 4 == 0:
            enemies.append(cls.create(team, spawn_x, spawn_y - 50, "tank"))

        return enemies

class ProjectileFactory:
    _TYPES: dict = {
        "basic": {"speed": 7.0, "damage": 25},
        "heavy": {"speed": 4.0, "damage": 60},
        "rapid": {"speed": 10.0, "damage": 12},
    }

    @classmethod
    def create(cls, owner_name, team, x, y, dx, dy, proj_type="basic") -> Projectile:
        params = cls._TYPES.get(proj_type, cls._TYPES["basic"])
        return Projectile(owner_name=owner_name, team=team, x=x, y=y, dx=dx, dy=dy, **params)