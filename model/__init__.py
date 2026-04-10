"""
model/__init__.py
Exporta las clases e interfaces públicas del paquete model.
Las otras personas importan desde aquí: from model import Player, GameState, ...
"""

from model.interfaces  import IDamageable, IMovable, ISerializable
from model.player      import Player
from model.enemy       import Enemy
from model.castle      import Castle
from model.projectile  import Projectile
from model.factories   import EnemyFactory, ProjectileFactory
from model.game_state  import (
    GameState,
    EVENT_ENEMY_KILLED,
    EVENT_CASTLE_DAMAGED,
    EVENT_GAME_OVER,
    EVENT_PROJECTILE_HIT,
)

__all__ = [
    # Interfaces
    "IDamageable",
    "IMovable",
    "ISerializable",
    # Entidades
    "Player",
    "Enemy",
    "Castle",
    "Projectile",
    # Factories
    "EnemyFactory",
    "ProjectileFactory",
    # Estado central
    "GameState",
    # Eventos Observer
    "EVENT_ENEMY_KILLED",
    "EVENT_CASTLE_DAMAGED",
    "EVENT_GAME_OVER",
    "EVENT_PROJECTILE_HIT",
]