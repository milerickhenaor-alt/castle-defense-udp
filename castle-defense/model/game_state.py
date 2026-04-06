from __future__ import annotations
import time
import random
from typing import Callable, Dict, List, Optional

from model.castle      import Castle
from model.enemy       import Enemy
from model.player      import Player
from model.projectile  import Projectile
from model.factories   import EnemyFactory

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES DE EVENTOS
# ─────────────────────────────────────────────────────────────────────────────
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
    """
    Gestiona la lógica central, colisiones y sincronización de red.
    """
    _instance: Optional[GameState] = None

    @classmethod
    def get_instance(cls) -> "GameState":
        if cls._instance is None:
            raise RuntimeError("GameState no inicializado.")
        return cls._instance

    def __init__(
        self,
        players: List[Player],
        castles: Dict[str, Castle],
        enemy_types: Dict[str, str], # Formato: {"A": "Troll 1", "B": "Troll 3"}
        map_width: int = 1000,
        map_height: int = 600,
        enemy_spawn_interval: float = 8.0,
        game_duration: float = 180.0
    ) -> None:
        GameState._instance = self
        
        # Entidades
        self.players: Dict[str, Player] = {p.name: p for p in players}
        self.castles: Dict[str, Castle] = castles
        self.enemy_types = enemy_types 
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []

        # Configuración de mapa y tiempo
        self.map_width = map_width
        self.map_height = map_height
        self._start_time = time.time()
        self._last_spawn_time = 0 
        self.enemy_spawn_interval = enemy_spawn_interval
        self.max_enemies_on_screen = 6
        self.game_duration = game_duration
        
        # Estado del juego
        self.running = True
        self.winner_team = ""

        # Sistema de Observer
        self._listeners: Dict[str, List[Callable]] = {event: [] for event in _ALL_EVENTS}

    # ── SISTEMA DE EVENTOS ─────────────────────────────────────────── #

    def subscribe(self, event: str, callback: Callable):
        if event in self._listeners:
            self._listeners[event].append(callback)

    def _emit(self, event: str, payload: dict):
        for cb in self._listeners.get(event, []):
            cb(payload)

    @property
    def remaining_time(self) -> float:
        return max(0.0, self.game_duration - (time.time() - self._start_time))

    # ── UPDATE Y LÓGICA ────────────────────────────────────────────── #

    def update(self) -> None:
        if not self.running:
            return

        self._spawn_enemies()
        self._update_movables() 
        self._check_collisions()
        self._check_game_over()

    def update_from_server(self, network_data: dict):
        """
        Sincroniza el estado local con los datos recibidos del socket.
        """
        # 1. Sincronizar Jugadores (Posición y Score)
        for p_data in network_data.get("players", []):
            name = p_data["name"]
            if name in self.players:
                # No actualizamos 'nuestro' jugador para evitar lag visual (opcional)
                self.players[name].x = p_data["x"]
                self.players[name].y = p_data["y"]
                self.players[name].score = p_data.get("score", self.players[name].score)

        # 2. Sincronizar Enemigos (Trolls) por ID
        if "enemies" in network_data:
            new_enemies_list = []
            for e_data in network_data["enemies"]:
                # Buscar si el enemigo ya existe para mantener su instancia
                existing = next((e for e in self.enemies if e.id == e_data["id"]), None)
                if existing:
                    existing.x, existing.y = e_data["x"], e_data["y"]
                    existing.hp = e_data.get("hp", existing.hp)
                    existing.state = e_data.get("state", existing.state)
                    new_enemies_list.append(existing)
                else:
                    # Crear nuevo enemigo si no existía en nuestro cliente
                    # Import local para evitar colisión circular
                    from model.enemy import Enemy
                    ne = Enemy(e_data["id"], e_data["team"], e_data["type"], e_data["x"], e_data["y"])
                    new_enemies_list.append(ne)
            self.enemies = new_enemies_list

    def _spawn_enemies(self) -> None:
        """ Genera Trolls basados en la selección de cada equipo """
        now = time.time()
        if now - self._last_spawn_time < self.enemy_spawn_interval: return
        if len(self.enemies) >= self.max_enemies_on_screen: return

        self._last_spawn_time = now
        opcion = random.randint(1, 3) # 1: Equipo A, 2: Equipo B, 3: Ambos
        X_IZQ, X_DER = 180, 820

        # Spawn para Equipo A (Izquierda)
        if opcion in [1, 3]:
            tipo_a = self.enemy_types.get("A", "Troll 1")
            y_pos = random.randint(350, 500)
            self.enemies.append(EnemyFactory.create("A", X_IZQ, y_pos, tipo_a))
        
        # Spawn para Equipo B (Derecha)
        if opcion in [2, 3]:
            tipo_b = self.enemy_types.get("B", "Troll 1")
            y_pos = random.randint(350, 500)
            self.enemies.append(EnemyFactory.create("B", X_DER, y_pos, tipo_b))

    def _update_movables(self) -> None:
        """ Mueve enemigos y gestiona ataques a los castillos """
        MURO_DER, MURO_IZQ = 827, 177
        
        for enemy in self.enemies:
            if not enemy.is_alive: continue
            
            # Lógica de dirección y objetivo según equipo
            if enemy.team == "A":
                llegó = enemy.x >= MURO_DER
                target_castle = self.castles["B"]
            else:
                llegó = enemy.x <= MURO_IZQ
                target_castle = self.castles["A"]

            if llegó:
                enemy.speed = 0
                enemy.state = "attacking"
                # Aplicar daño al castillo
                target_castle.take_damage(enemy.damage * 0.01)
                self._emit(EVENT_CASTLE_DAMAGED, {
                    "team": "B" if enemy.team == "A" else "A",
                    "hp": target_castle.hp
                })
            else:
                enemy.state = "walking"
                enemy.update()

    def _check_collisions(self) -> None:
        """ Colisión Proyectil -> Enemigo """
        for proj in self.projectiles:
            if not proj.active: continue
            for enemy in self.enemies:
                if not enemy.is_alive or proj.team == enemy.team: 
                    continue 
                
                if proj.collides_with(enemy.x, enemy.y, enemy.width, enemy.height):
                    killed = enemy.take_damage(proj.damage)
                    proj.deactivate()
                    self._emit(EVENT_PROJECTILE_HIT, {"enemy": enemy})
                    
                    if killed:
                        # Dar puntos al dueño del proyectil
                        killer = self.players.get(proj.owner_name)
                        if killer: killer.add_score(enemy.reward)
                        self._emit(EVENT_ENEMY_KILLED, {"enemy": enemy, "killer": proj.owner_name})

    def _check_game_over(self) -> None:
        """ Verifica si un castillo cayó o el tiempo terminó """
        # Por destrucción
        for team, castle in self.castles.items():
            if castle.is_destroyed:
                self.running = False
                self.winner_team = "B" if team == "A" else "A"
                self._emit(EVENT_GAME_OVER, {"winner": self.winner_team})
                return

        # Por tiempo
        if self.remaining_time <= 0:
            self.running = False
            # Ganador por Score total de equipo
            score_a = sum(p.score for p in self.players.values() if p.team == "A")
            score_b = sum(p.score for p in self.players.values() if p.team == "B")
            self.winner_team = "A" if score_a > score_b else "B"
            self._emit(EVENT_GAME_OVER, {"winner": self.winner_team})

    # ── UTILIDADES ─────────────────────────────────────────────────── #

    def add_projectile(self, proj: Projectile):
        self.projectiles.append(proj)

    def to_dict(self) -> dict:
        """ Serializa el estado para enviarlo por red si fuera necesario """
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
                } for e in self.enemies
            ],
            "remaining_time": self.remaining_time
        }