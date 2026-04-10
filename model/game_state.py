from __future__ import annotations
import time
import random
from typing import Dict, List, Optional, Union, Callable

from model.castle      import Castle
from model.enemy       import Enemy
from model.player      import Player
from model.projectile   import Projectile
from model.factories   import EnemyFactory

# --- CONSTANTES DE EVENTOS ---
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
        enemy_spawn_interval: float = 5.0,
        game_duration: float = 180.0
    ) -> None:
        GameState._instance = self
        
        # Jugadores y Castillos
        self.players: Dict[str, Player] = {p.name: p for p in players}
        self.castles: Dict[str, Castle] = castles
        self.enemy_types = enemy_types 
        
        # Entidades dinámicas
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []

        # Configuración de mapa y tiempo
        self.map_width = map_width
        self.map_height = map_height
        self._start_time = time.time()
        self._last_spawn_time = 0 
        self.enemy_spawn_interval = enemy_spawn_interval
        self.max_enemies_on_screen = 10
        self.game_duration = game_duration
        
        # Estado de partida
        self.running = True
        self.winner_team = ""
        self.local_players = set() # Nombres de jugadores en esta PC

        # Sistema de listeners para eventos
        self._listeners: Dict[str, List[Callable]] = {event: [] for event in _ALL_EVENTS}

    # ---------------- SISTEMA DE SINCRONIZACIÓN (RED) ---------------- #

    def update_from_server(self, network_data: Union[dict, list]):
        """Actualiza el estado local con datos del servidor sin romperse por tipos de datos."""
        if not network_data:
            return

        players_data = []
        is_full_sync = False

        # Diferenciar si viene una lista (solo posiciones) o dict (estado completo)
        if isinstance(network_data, list):
            players_data = network_data
        elif isinstance(network_data, dict):
            players_data = network_data.get("players", [])
            is_full_sync = True

        # 1. Sincronizar Jugadores
        for p_info in players_data:
            name = p_info.get("name")
            if name in self.players:
                # No sobrescribir posición si es el jugador que yo controlo (evita jitter)
                if name not in self.local_players:
                    self.players[name].x = float(p_info.get("x", self.players[name].x))
                    self.players[name].y = float(p_info.get("y", self.players[name].y))
                self.players[name].score = p_info.get("score", self.players[name].score)

        # 2. Sincronizar Enemigos y Castillos (Solo en dict completo)
        if is_full_sync:
            # Sincronizar HP de Castillos
            if "castles" in network_data:
                for team, c_info in network_data["castles"].items():
                    if team in self.castles:
                        self.castles[team].hp = c_info.get("hp", self.castles[team].hp)

            # Sincronizar Lista de Enemigos
            if "enemies" in network_data:
                updated_enemies = []
                for e_info in network_data["enemies"]:
                    # Buscar si el enemigo ya existe para actualizarlo
                    existing = next((e for e in self.enemies if e.id == e_info["id"]), None)
                    if existing:
                        existing.x = float(e_info["x"])
                        existing.y = float(e_info["y"])
                        existing.hp = e_info["hp"]
                        existing.state = e_info.get("state", "walking")
                        updated_enemies.append(existing)
                    else:
                        # Si es nuevo, usar la Factory para crearlo localmente
                        try:
                            new_enemy = Enemy(
                                team=e_info["team"],
                                x=float(e_info["x"]),
                                y=float(e_info["y"]),
                                type=e_info.get("type", "Troll 1"),
                                hp=e_info.get("hp", 100),
                                max_hp=100,
                                state=e_info.get("state", "walking")
                            )
                            new_enemy.id = e_info["id"]
                            updated_enemies.append(new_enemy)
                        except Exception as e:
                            print(f"Error creando enemigo en cliente: {e}")
                
                self.enemies = updated_enemies

    # ---------------- LÓGICA DE JUEGO (SERVIDOR) ---------------- #

    def update_server(self) -> None:
        """Solo corre en el servidor para procesar física y reglas."""
        if not self.running: return
        self._spawn_enemies()
        self._update_movables()
        self._check_collisions()
        self._check_game_over()

    def update_client(self) -> None:
        """Corre en el cliente (puedes añadir interpolación aquí)."""
        pass

    def _spawn_enemies(self) -> None:
        print("🔥 INTENTANDO SPAWN")
        now = time.time()
        if now - self._last_spawn_time < self.enemy_spawn_interval: return
        if len(self.enemies) >= self.max_enemies_on_screen: return

        self._last_spawn_time = now
        
        # Puntos de spawn: Salen de los castillos
        SPAWN_X_A = 150
        SPAWN_X_B = 850
        
        opcion = random.randint(1, 3) # 1: Equipo A, 2: Equipo B, 3: Ambos

        if opcion in [1, 3]:
            tipo = self.enemy_types.get("A", "Troll 1")
            self.enemies.append(EnemyFactory.create("A", SPAWN_X_A, random.randint(350, 450), tipo))
        
        if opcion in [2, 3]:
            tipo = self.enemy_types.get("B", "Troll 1")
            self.enemies.append(EnemyFactory.create("B", SPAWN_X_B, random.randint(350, 450), tipo))

    def _update_movables(self) -> None:
        # Los enemigos se mueven hacia el castillo enemigo
        for enemy in self.enemies:
            if not enemy.is_alive: continue
            
            # Límites de colisión con los castillos
            if enemy.team == "A":
                llegó = enemy.x >= 830 # Cerca del castillo B
                target = self.castles["B"]
            else:
                llegó = enemy.x <= 170 # Cerca del castillo A
                target = self.castles["A"]

            if llegó:
                enemy.speed = 0
                enemy.state = "attacking"
                target.take_damage(0.05) # Daño por frame de ataque
            else:
                enemy.state = "walking"
                enemy.update() # Mueve al enemigo según su velocidad

    def _check_collisions(self) -> None:
        for proj in self.projectiles:
            if not proj.active: continue
            for enemy in self.enemies:
                if not enemy.is_alive or proj.team == enemy.team: continue
                
                # Colisión simple por radio/distancia
                if proj.collides_with(enemy.x, enemy.y, 40, 40):
                    killed = enemy.take_damage(proj.damage)
                    proj.deactivate()
                    if killed:
                        killer = self.players.get(proj.owner_name)
                        if killer: killer.add_score(20)

    def _check_game_over(self) -> None:
        # Victoria por destrucción de castillo
        for team, castle in self.castles.items():
            if castle.hp <= 0:
                self.running = False
                self.winner_team = "B" if team == "A" else "A"
                return

        # Victoria por tiempo (puntos)
        if self.remaining_time <= 0:
            self.running = False
            score_a = sum(p.score for p in self.players.values() if p.team == "A")
            score_b = sum(p.score for p in self.players.values() if p.team == "B")
            self.winner_team = "A" if score_a > score_b else "B"

    @property
    def remaining_time(self) -> float:
        return max(0.0, self.game_duration - (time.time() - self._start_time))

    def to_dict(self) -> dict:
        """Serializa el estado para enviarlo por red."""
        return {
            "players": [p.to_dict() for p in self.players.values()],
            "enemies": [
                {
                    "id": e.id, "x": e.x, "y": e.y, "team": e.team, 
                    "type": e.type, "hp": e.hp, "state": e.state
                } for e in self.enemies
            ],
            "castles": {t: {"hp": c.hp} for t, c in self.castles.items()},
            "remaining_time": self.remaining_time,
            "running": self.running,
            "winner": self.winner_team
        }