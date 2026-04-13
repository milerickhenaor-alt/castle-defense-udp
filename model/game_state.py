from __future__ import annotations
import time
import random
from typing import Dict, List, Optional

from model.castle import Castle
from model.enemy import Enemy
from model.player import Player
from model.projectile import Projectile
from model.factories import EnemyFactory

# AGREGA ESTO AQUÍ (Asegúrate de que no tengan espacios a la izquierda)
EVENT_ENEMY_KILLED    = "enemy_killed"
EVENT_CASTLE_DAMAGED  = "castle_damaged"
EVENT_GAME_OVER       = "game_over"
EVENT_PROJECTILE_HIT  = "projectile_hit"

_ALL_EVENTS = (
    EVENT_ENEMY_KILLED, 
    EVENT_CASTLE_DAMAGED, 
    EVENT_GAME_OVER, 
    EVENT_PROJECTILE_HIT
)


class GameState:
    def __init__(
        self,
        players: List[Player],
        castles: Dict[str, Castle],
        enemy_types: Dict[str, str],
        map_width: int = 1000,
        map_height: int = 600,
        enemy_spawn_interval: float = 5.0,
        game_duration: float = 180.0
    ):

        self.players = {p.name: p for p in players}
        self.castles = castles
        self.enemy_types = enemy_types

        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []

        self.map_width = map_width
        self.map_height = map_height

        self._start_time = time.time()
        self._last_spawn_time = 0
        self.enemy_spawn_interval = enemy_spawn_interval
        self.max_enemies_on_screen = 10
        self.game_duration = game_duration

        self.running = True
        self.winner_team = ""

    # ---------------- SERVER LOOP ---------------- #

    def update_server(self):
        if not self.running:
            return

        self._spawn_enemies()
        self._update_projectiles()
        self._update_enemies()
        self._check_collisions()
        self._check_game_over()

    # ASEGÚRATE DE QUE ESTO ESTÉ ALINEADO CON EL 'def' DE ARRIBA
    def update_client(self) -> None:
        """Corre en el cliente."""
        pass

    # ---------------- PROJECTILES ---------------- #

    def _update_projectiles(self):
        for p in self.projectiles:
            if not p.active:
                continue

            p.update()

            if p.is_out_of_bounds(self.map_width, self.map_height):
                p.deactivate()

        self.projectiles = [p for p in self.projectiles if p.active]

    # ---------------- ENEMIES ---------------- #

    def _spawn_enemies(self):
        now = time.time()

        if now - self._last_spawn_time < self.enemy_spawn_interval:
            return

        if len(self.enemies) >= self.max_enemies_on_screen:
            return

        self._last_spawn_time = now

        SPAWN_X_A = 150
        SPAWN_X_B = 850

        option = random.randint(1, 3)

        if option in [1, 3]:
            self.enemies.append(
                EnemyFactory.create("A", SPAWN_X_A, random.randint(350, 450), "Troll 1")
            )

        if option in [2, 3]:
            self.enemies.append(
                EnemyFactory.create("B", SPAWN_X_B, random.randint(350, 450), "Troll 1")
            )

    def _update_enemies(self):
        for e in self.enemies:
            if not e.is_alive:
                continue

            if e.team == "A":
                if e.x >= 830:
                    self.castles["B"].take_damage(0.05)
                    e.speed = 0
                else:
                    e.update()
            else:
                if e.x <= 170:
                    self.castles["A"].take_damage(0.05)
                    e.speed = 0
                else:
                    e.update()

    # ---------------- COLLISIONS ---------------- #

    def _check_collisions(self):
        for proj in self.projectiles:
            if not proj.active:
                continue

            for enemy in self.enemies:
                if not enemy.is_alive:
                    continue

                if proj.team == enemy.team:
                    continue

                if proj.collides_with(enemy.x, enemy.y, 60, 60):
                    killed = enemy.take_damage(proj.damage)
                    proj.deactivate()

                    if killed:
                        player = self.players.get(proj.owner_name)
                        if player:
                            player.add_score(20)

    # ---------------- GAME OVER ---------------- #

    def _check_game_over(self):
        for team, castle in self.castles.items():
            if castle.hp <= 0:
                self.running = False
                self.winner_team = "B" if team == "A" else "A"

        if self.remaining_time <= 0:
            self.running = False

    @property
    def remaining_time(self):
        return max(0.0, self.game_duration - (time.time() - self._start_time))

    # ---------------- NETWORK ---------------- #

    def to_dict(self):
        return {
            "players": [p.to_dict() for p in self.players.values()],
            "enemies": [
                {
                    "id": e.id,
                    "x": e.x,
                    "y": e.y,
                    "team": e.team,
                    "type": e.type,
                    "hp": e.hp,
                    "state": e.state
                }
                for e in self.enemies
            ],
            "projectiles": [p.to_dict() for p in self.projectiles],
            "castles": {t: {"hp": c.hp} for t, c in self.castles.items()},
            "remaining_time": self.remaining_time,
            "running": self.running,
            "winner": self.winner_team
        }
    
    # --- Agrégalo al final de la clase GameState en model/game_state.py ---

    def update_from_dict(self, data: dict):
        """Actualiza el estado local con los datos recibidos del servidor."""
        if not data:
            return

        # 1. Actualizar Jugadores
        for p_data in data.get("players", []):
            name = p_data.get("name")
            if name in self.players:
                self.players[name].x = p_data.get("x")
                self.players[name].y = p_data.get("y")
                self.players[name].score = p_data.get("score", 0)

        self.enemies = []
        for e_data in data.get("enemies", []):
            # Aquí está el truco: verifica si tu clase Enemy usa 'enemy_type' o 'type'
            # Por lo que veo en el error, 'enemy_type' NO es el nombre correcto.
            enemy = Enemy(
                id=e_data["id"],
                team=e_data["team"],
                x=e_data["x"],
                y=e_data["y"]
                # Quitamos el nombre del argumento 'enemy_type=' para evitar el error
            )
            # Si necesitas pasarle el tipo, asígnale el valor después:
            enemy.type = e_data.get("type", "Troll 1") 
            enemy.hp = e_data.get("hp", 100)
            self.enemies.append(enemy)

        # 3. Actualizar Proyectiles
        self.projectiles = []
        for p_data in data.get("projectiles", []):
            # Determinamos la dirección según el equipo para que no falten dx y dy
            # Si el equipo es A, dx es 1 (derecha). Si es B, dx es -1 (izquierda).
            d_x = 1 if p_data.get("team") == "A" else -1
            d_y = 0 
            
            proj = Projectile(
                x=p_data["x"], 
                y=p_data["y"], 
                team=p_data["team"], 
                owner_name=p_data.get("owner_name", "unknown"),
                dx=d_x,  # <--- Agregado
                dy=d_y   # <--- Agregado
            )
            proj.active = p_data.get("active", True)
            self.projectiles.append(proj)

        # 4. Actualizar Castillos
        castles_data = data.get("castles", {})
        for team, c_data in castles_data.items():
            if team in self.castles:
                self.castles[team].hp = c_data.get("hp", 100)

        # 5. Datos generales
        self.running = data.get("running", True)
        self.winner_team = data.get("winner", "")