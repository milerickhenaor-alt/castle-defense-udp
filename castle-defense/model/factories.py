from __future__ import annotations
from model.enemy      import Enemy
from model.projectile import Projectile

import uuid

import uuid
from model.enemy import Enemy

class EnemyFactory:
    """
    Crea instancias de Enemy con configuración balanceada.
    Mapea los nombres del servidor (Trolls) a las estadísticas locales.
    """
    # Estadísticas base (Asegúrate de que coincidan con los campos de Enemy)
    _STATS = {
        "normal": {"hp": 100, "max_hp": 100, "speed": 0.6, "damage": 20, "reward": 10, "width": 32.0, "height": 32.0},
        "fast":   {"hp": 50,  "max_hp": 50,  "speed": 1.1, "damage": 10, "reward": 15, "width": 24.0, "height": 24.0},
        "tank":   {"hp": 250, "max_hp": 250, "speed": 0.3, "damage": 40, "reward": 30, "width": 48.0, "height": 48.0},
    }

    # 🔥 MAPEO: Traduce lo que viene del servidor a tus tipos internos
    _NAME_MAP = {
        "Troll 1": "normal",
        "Troll 2": "tank",
        "Troll 3": "fast"
    }

    @classmethod
    def create(cls, team: str, spawn_x: float, spawn_y: float, enemy_type: str = "Troll 1") -> Enemy:
        # 1. Traducir el nombre si es un Troll, si no usar el original
        internal_type = cls._NAME_MAP.get(enemy_type, enemy_type)

        # 2. Validar que el tipo interno exista
        if internal_type not in cls._STATS:
            # print(f"⚠️ Advertencia: Tipo [{enemy_type}] no reconocido. Usando 'normal'.")
            internal_type = "normal"

        # 3. Obtener parámetros y generar ID único
        params = cls._STATS[internal_type]
        enemy_id = str(uuid.uuid4())[:8]

        # 4. Crear instancia. 
        # IMPORTANTE: Pasamos los obligatorios primero (team, x, y)
        # y luego los opcionales mediante **params y argumentos nombrados.
        return Enemy(
            team=team,
            x=spawn_x,
            y=spawn_y,
            type=enemy_type,  # El nombre real del troll para el Renderer
            id=enemy_id,
            **params
        )

    @classmethod
    def create_wave(cls, team, spawn_x, spawn_y, wave_number=1):
        """Mantiene compatibilidad con oleadas si las usas localmente"""
        enemies = []
        enemies.append(cls.create(team, spawn_x, spawn_y, "Troll 1"))

        if wave_number >= 3 and wave_number % 2 == 0:
            enemies.append(cls.create(team, spawn_x, spawn_y + 50, "Troll 3"))
        
        if wave_number >= 5 and wave_number % 4 == 0:
            enemies.append(cls.create(team, spawn_x, spawn_y - 50, "Troll 2"))

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