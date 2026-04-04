"""
model/factories.py
Persona 1 — Model Core

Patrón de diseño: Factory Method
---------------------------------
¿Por qué Factory Method aquí?

El problema sin Factory:
    Si en game_state.py, el controller, o la red necesitan crear un Enemy
    o un Projectile, tendrían que conocer todos los parámetros concretos
    (posición de spawn, velocidad, daño, etc.) y duplicar esa lógica
    en múltiples lugares. Cualquier cambio en los valores requeriría
    editar varios archivos.

La solución con Factory:
    EnemyFactory y ProjectileFactory centralizan la lógica de creación.
    El resto del sistema solo llama a EnemyFactory.create("A") y obtiene
    un Enemy correctamente configurado, sin saber cómo se construye.

Beneficios concretos en este proyecto:
    - OCP: agregar un nuevo tipo de enemigo (ej: "fast_troll") no modifica
      el código existente, solo agrega un nuevo método/registro en la factory.
    - DRY: los valores de velocidad, daño y vida están en un único lugar.
    - Testabilidad: se puede mockear la factory para pruebas unitarias.
"""

from __future__ import annotations
from model.enemy      import Enemy
from model.projectile import Projectile


# ─────────────────────────────────────────────────────────────────────────────
# EnemyFactory
# ─────────────────────────────────────────────────────────────────────────────

class EnemyFactory:
    """
    Crea instancias de Enemy con configuración predefinida.

    Tipos disponibles
    -----------------
    "normal"  → troll estándar (velocidad y vida medias)
    "fast"    → troll rápido (menos vida, más velocidad)
    "tank"    → troll lento (mucha vida, mucho daño)
    """

    # Registro de tipos: cada entrada define los parámetros del Enemy.
    # Agregar un tipo nuevo = agregar una entrada aquí. Nada más cambia.
    _TYPES: dict = {
        "normal": {"hp": 100, "max_hp": 100, "speed": 1.5, "damage": 50,  "reward": 10, "width": 32.0, "height": 32.0},
        "fast":   {"hp":  60, "max_hp":  60, "speed": 3.0, "damage": 30,  "reward": 15, "width": 24.0, "height": 24.0},
        "tank":   {"hp": 300, "max_hp": 300, "speed": 0.8, "damage": 150, "reward": 30, "width": 48.0, "height": 48.0},
    }

    @classmethod
    def create(
        cls,
        team: str,
        spawn_x: float,
        spawn_y: float,
        enemy_type: str = "normal",
    ) -> Enemy:
        """
        Crea un Enemy del tipo indicado en la posición de spawn.

        Parameters
        ----------
        team        : 'A' | 'B'
        spawn_x/y   : posición inicial (normalmente junto al castillo)
        enemy_type  : 'normal' | 'fast' | 'tank'

        Returns
        -------
        Enemy listo para agregarse al GameState.

        Raises
        ------
        ValueError si el tipo no existe.
        """
        if enemy_type not in cls._TYPES:
            raise ValueError(
                f"Tipo de enemigo desconocido: {enemy_type!r}. "
                f"Opciones válidas: {list(cls._TYPES.keys())}"
            )

        params = cls._TYPES[enemy_type]
        return Enemy(
            team=team,
            x=spawn_x,
            y=spawn_y,
            **params,
        )

    @classmethod
    def create_wave(
        cls,
        team: str,
        spawn_x: float,
        spawn_y: float,
        wave_number: int = 1,
    ) -> list[Enemy]:
        """
        Genera una oleada de enemigos que escala con el número de ronda.
        Útil para que el GameState la llame en su spawn callback.

        wave 1    → 1 normal
        wave 2–3  → 1 normal + 1 fast
        wave 4+   → 1 normal + 1 fast + 1 tank
        """
        enemies = [cls.create(team, spawn_x, spawn_y, "normal")]
        if wave_number >= 2:
            enemies.append(cls.create(team, spawn_x, spawn_y + 50, "fast"))
        if wave_number >= 4:
            enemies.append(cls.create(team, spawn_x, spawn_y + 100, "tank"))
        return enemies


# ─────────────────────────────────────────────────────────────────────────────
# ProjectileFactory
# ─────────────────────────────────────────────────────────────────────────────

class ProjectileFactory:
    """
    Crea instancias de Projectile con configuración predefinida.

    Tipos disponibles
    -----------------
    "basic"   → disparo normal
    "heavy"   → más daño, más lento
    "rapid"   → menos daño, más rápido
    """

    _TYPES: dict = {
        "basic": {"speed": 10.0, "damage": 25},
        "heavy": {"speed":  6.0, "damage": 60},
        "rapid": {"speed": 16.0, "damage": 12},
    }

    @classmethod
    def create(
        cls,
        owner_name: str,
        team: str,
        x: float,
        y: float,
        dx: float,
        dy: float,
        proj_type: str = "basic",
    ) -> Projectile:
        """
        Crea un Projectile del tipo indicado.

        Parameters
        ----------
        owner_name  : nombre del jugador que disparó
        team        : equipo del jugador ('A' | 'B')
        x, y        : posición de origen (normalmente la del jugador)
        dx, dy      : dirección normalizada del disparo
        proj_type   : 'basic' | 'heavy' | 'rapid'

        Returns
        -------
        Projectile listo para agregarse al GameState.
        """
        if proj_type not in cls._TYPES:
            raise ValueError(
                f"Tipo de proyectil desconocido: {proj_type!r}. "
                f"Opciones válidas: {list(cls._TYPES.keys())}"
            )

        params = cls._TYPES[proj_type]
        return Projectile(
            owner_name=owner_name,
            team=team,
            x=x,
            y=y,
            dx=dx,
            dy=dy,
            **params,
        )