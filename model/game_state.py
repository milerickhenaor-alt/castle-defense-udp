from __future__ import annotations
import time
import random
from typing import Dict, List, Optional, Union

from model.castle      import Castle
from model.enemy       import Enemy
from model.player      import Player
from model.projectile   import Projectile
from model.factories   import EnemyFactory

class GameState:
    _instance: Optional["GameState"] = None

    @classmethod
    def get_instance(cls) -> "GameState":
        if cls._instance is None:
            raise RuntimeError("GameState no inicializado.")
        return cls._instance

    def __init__(
        self,
        players: List[Player],
        castles: Dict[str, Castle],
        enemy_types: Dict[str, str],
        map_width: int = 1000,
        map_height: int = 600,
        enemy_spawn_interval: float = 5.0, # Bajado a 5s para más acción
        game_duration: float = 180.0
    ) -> None:
        GameState._instance = self
        
        self.players: Dict[str, Player] = {p.name: p for p in players}
        self.castles: Dict[str, Castle] = castles
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
        self.local_players = set() 

    # ---------------- SYNC (CORREGIDO) ---------------- #

    def update_from_server(self, network_data: Union[dict, list]):
        """Maneja actualizaciones evitando el error de 'list object has no attribute get'."""
        if not network_data:
            return

        players_list = []
        full_state = False

        # --- VALIDACIÓN DE TIPO ---
        if isinstance(network_data, list):
            # Si es una lista, el servidor solo mandó movimientos de jugadores
            players_list = network_data
        elif isinstance(network_data, dict):
            # Si es dict, es el estado completo (con enemigos y castillos)
            players_list = network_data.get("players", [])
            full_state = True

        # Actualizar Jugadores
        for p_data in players_list:
            name = p_data.get("name")
            if name in self.players:
                if name not in self.local_players:
                    self.players[name].x = float(p_data.get("x", self.players[name].x))
                    self.players[name].y = float(p_data.get("y", self.players[name].y))
                self.players[name].score = p_data.get("score", self.players[name].score)

        # Actualizar Enemigos y Castillos (Solo si el paquete es completo)
        if full_state:
            if "enemies" in network_data:
                new_enemies = []
                for e_data in network_data["enemies"]:
                    try:
                        existing = next((e for e in self.enemies if e.id == e_data["id"]), None)
                        if existing:
                            existing.x = float(e_data["x"])
                            existing.y = float(e_data["y"])
                            existing.hp = e_data["hp"]
                            existing.state = e_data.get("state", "walking")
                            new_enemies.append(existing)
                        else:
                            ne = Enemy(
                                team=e_data["team"],
                                x=float(e_data["x"]),
                                y=float(e_data["y"]),
                                type=e_data.get("type", "Troll 1"),
                                hp=e_data.get("hp", 100),
                                max_hp=e_data.get("hp", 100),
                                state=e_data.get("state", "walking")
                            )
                            ne.id = e_data["id"]
                            new_enemies.append(ne)
                    except Exception as e:
                        print(f"⚠️ Error sync Enemy: {e}")
                self.enemies = new_enemies

            if "castles" in network_data:
                for team, c_data in network_data["castles"].items():
                    if team in self.castles:
                        self.castles[team].hp = c_data["hp"]

    # ---------------- LOGIC (SERVER SIDE) ---------------- #

    def update_server(self) -> None:
        if not self.running: return
        self._spawn_enemies()
        self._update_movables()
        self._check_collisions()
        self._check_game_over()

    def update_client(self) -> None:
        """Lógica del lado del cliente."""
        pass

    def _spawn_enemies(self) -> None:
        now = time.time()
        if now - self._last_spawn_time < self.enemy_spawn_interval: return
        if len(self.enemies) >= self.max_enemies_on_screen: return

        self._last_spawn_time = now
        
        # Puntos de spawn frente a los castillos
        SPAWN_X_A = 150
        SPAWN_X_B = 850
        
        opcion = random.randint(1, 3)

        if opcion in [1, 3]:
            tipo_a = self.enemy_types.get("A", "Troll 1")
            self.enemies.append(EnemyFactory.create("A", SPAWN_X_A, random.randint(350, 500), tipo_a))
        
        if opcion in [2, 3]:
            tipo_b = self.enemy_types.get("B", "Troll 1")
            self.enemies.append(EnemyFactory.create("B", SPAWN_X_B, random.randint(350, 500), tipo_b))

    def _update_movables(self) -> None:
        # Los trolls caminan hacia el castillo contrario
        MURO_DER, MURO_IZQ = 830, 170
        for enemy in self.enemies:
            if not enemy.is_alive: continue
            
            if enemy.team == "A":
                llegó = enemy.x >= MURO_DER
                target_castle = self.castles["B"]
            else:
                llegó = enemy.x <= MURO_IZQ
                target_castle = self.castles["A"]

            if llegó:
                enemy.speed = 0
                enemy.state = "attacking"
                target_castle.take_damage(0.1) # Daño constante al castillo
            else:
                enemy.state = "walking"
                enemy.update()

    def _check_collisions(self) -> None:
        for proj in self.projectiles:
            if not proj.active: continue
            for enemy in self.enemies:
                if not enemy.is_alive or proj.team == enemy.team: continue
                if proj.collides_with(enemy.x, enemy.y, 40, 40):
                    killed = enemy.take_damage(proj.damage)
                    proj.deactivate()
                    if killed:
                        killer = self.players.get(proj.owner_name)
                        if killer: killer.add_score(20)

    def _check_game_over(self) -> None:
        for team, castle in self.castles.items():
            if castle.hp <= 0:
                self.running = False
                self.winner_team = "B" if team == "A" else "A"

    @property
    def remaining_time(self) -> float:
        return max(0.0, self.game_duration - (time.time() - self._start_time))

    def to_dict(self) -> dict:
        return {
            "players": [p.to_dict() for p in self.players.values()],
            "enemies": [{"id": e.id, "x": e.x, "y": e.y, "team": e.team, "type": e.type, "hp": e.hp, "state": e.state} for e in self.enemies],
            "castles": {t: {"hp": c.hp} for t, c in self.castles.items()},
            "remaining_time": self.remaining_time
        }