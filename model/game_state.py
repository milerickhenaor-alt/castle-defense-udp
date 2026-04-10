"""
model/game_state.py

Patrones de diseño aplicados
-----------------------------
1. Singleton
   ¿Por qué?
       Solo puede existir un estado de juego por proceso. Si el controller
       y la red crearan instancias distintas, habría dos fuentes de verdad
       inconsistentes.
   ¿Cómo?
       GameState guarda su instancia en _instance. El constructor la asigna
       al crearse. GameState.get_instance() la devuelve desde cualquier módulo.

2. Observer
   ¿Por qué?
       El modelo necesita notificar eventos a otras capas (controller, red,
       sonido) sin depender de ellas directamente.
   ¿Cómo?
       GameState mantiene un dict de listas de callbacks por evento.
       Cualquier módulo externo se suscribe con subscribe(evento, fn).

3. Factory Method (en factories.py)
   GameState delega la creación de enemies a EnemyFactory.
   OCP: cambiar cómo se generan los enemigos no modifica GameState.

Principios SOLID
----------------
SRP : GameState solo ejecuta la lógica del juego. Sin pygame, sin sockets.
      update_server() y update_client() separan responsabilidades de red.
OCP : Nuevos eventos se agregan al dict sin tocar el núcleo.
LSP : Opera sobre IDamageable e IMovable — no asume tipos concretos.
ISP : Consume solo las interfaces que necesita de cada entidad.
DIP : Depende de abstracciones (interfaces), no de clases concretas.
"""

from __future__ import annotations
import time
import random
from typing import Dict, List, Optional, Union, Callable

from model.castle      import Castle
from model.enemy       import Enemy
from model.player      import Player
from model.projectile  import Projectile
from model.factories   import EnemyFactory

# --- CONSTANTES DE EVENTOS (Observer) ---
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
    Motor de reglas del juego — Singleton + Observer.

    Gestiona y actualiza:
      • jugadores  (players)
      • castillos  (castles)
      • enemigos   (enemies)
      • proyectiles (projectiles)
      • puntajes, tiempo, estado de partida

    Sin ninguna dependencia de pygame, sockets o interfaz gráfica (SRP).
    """

    # ── Singleton ─────────────────────────────────────────────────────── #
    _instance: Optional["GameState"] = None

    @classmethod
    def get_instance(cls) -> "GameState":
        """
        [Singleton] Devuelve la instancia única del estado del juego.
        Lanza RuntimeError si aún no ha sido creada.
        """
        if cls._instance is None:
            raise RuntimeError("GameState no inicializado.")
        return cls._instance

    # ── Constructor ───────────────────────────────────────────────────── #

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
        # Singleton: registrar esta instancia
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
        self.local_players = set()  # Nombres de jugadores en esta PC

        # ── Observer: registro de listeners ─────────────────────────── #
        self._listeners: Dict[str, List[Callable]] = {
            event: [] for event in _ALL_EVENTS
        }

    # ── Observer — API pública ─────────────────────────────────────── #

    def subscribe(self, event: str, callback: Callable) -> None:
        """
        [Observer] Registra un listener para el evento indicado.

        Ejemplo:
            state.subscribe(EVENT_GAME_OVER, view.show_end_screen)
            state.subscribe(EVENT_ENEMY_KILLED, network.broadcast_kill)
        """
        if event in self._listeners:
            self._listeners[event].append(callback)

    def _emit(self, event: str, payload: dict) -> None:
        """
        [Observer] Notifica a todos los suscriptores de un evento.
        DIP: el modelo notifica sin conocer a los receptores.
        """
        for cb in self._listeners.get(event, []):
            cb(payload)

    # ── Sincronización (RED) ───────────────────────────────────────── #

    def update_from_server(self, network_data: Union[dict, list]) -> None:
        """
        Actualiza el estado local con datos del servidor.

        SRP: solo sincroniza datos — no ejecuta lógica del juego.
        Acepta lista (solo posiciones) o dict (estado completo).
        """
        if not network_data:
            return

        players_data = []
        is_full_sync = False

        if isinstance(network_data, list):
            players_data = network_data
        elif isinstance(network_data, dict):
            players_data = network_data.get("players", [])
            is_full_sync = True

        # 1. Sincronizar Jugadores
        for p_info in players_data:
            name = p_info.get("name")
            if name in self.players:
                # No sobrescribir posición si es el jugador local (evita jitter)
                if name not in self.local_players:
                    self.players[name].x = float(p_info.get("x", self.players[name].x))
                    self.players[name].y = float(p_info.get("y", self.players[name].y))
                self.players[name].score = p_info.get("score", self.players[name].score)

        # 2. Sincronizar Enemigos, Castillos y Estado (solo en dict completo)
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
                    existing = next((e for e in self.enemies if e.id == e_info["id"]), None)
                    if existing:
                        existing.x     = float(e_info["x"])
                        existing.y     = float(e_info["y"])
                        existing.hp    = e_info["hp"]
                        existing.state = e_info.get("state", "walking")
                        updated_enemies.append(existing)
                    else:
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

            # Sincronizar estado de fin de juego desde el servidor
            if "running" in network_data:
                self.running = network_data["running"]
            if "winner" in network_data:
                self.winner_team = network_data["winner"]

    # ── Lógica del juego ──────────────────────────────────────────── #

    def update_server(self) -> None:
        """
        Lógica que solo ejecuta el Servidor.
        SRP: el servidor es la única fuente de verdad del juego.
        """
        if not self.running:
            return
        self._spawn_enemies()    # Factory Method
        self._update_movables()  # LSP: opera sobre IMovable
        self._check_collisions() # LSP: opera sobre IDamageable
        self._check_game_over()

    def update_client(self) -> None:
        """
        Lógica que ejecuta el Cliente.
        Verifica game over localmente como respaldo si el servidor
        no notifica a tiempo.
        """
        if not self.running:
            return
        self._check_game_over()

    # ── Spawn de enemigos (Factory Method) ────────────────────────── #

    def _spawn_enemies(self) -> None:
        """
        Genera una oleada de trolls si pasó el intervalo de spawn.
        OCP: delega la construcción a EnemyFactory — agregar tipos
        de enemigos no modifica este método.
        """
        now = time.time()
        if now - self._last_spawn_time < self.enemy_spawn_interval:
            return
        if len(self.enemies) >= self.max_enemies_on_screen:
            return

        self._last_spawn_time = now

        SPAWN_X_A = 150
        SPAWN_X_B = 850

        opcion = random.randint(1, 3)

        if opcion in [1, 3]:
            tipo = self.enemy_types.get("A", "Troll 1")
            self.enemies.append(
                EnemyFactory.create("A", SPAWN_X_A, random.randint(350, 450), tipo)
            )

        if opcion in [2, 3]:
            tipo = self.enemy_types.get("B", "Troll 1")
            self.enemies.append(
                EnemyFactory.create("B", SPAWN_X_B, random.randint(350, 450), tipo)
            )

    # ── Movimiento (LSP: opera sobre IMovable) ─────────────────────── #

    def _update_movables(self) -> None:
        """
        Mueve los enemigos hacia el castillo contrario.
        LSP: llama enemy.update() — funciona con cualquier IMovable.
        """
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue

            if enemy.team == "A":
                llegó  = enemy.x >= 830
                target = self.castles["B"]
            else:
                llegó  = enemy.x <= 170
                target = self.castles["A"]

            if llegó:
                enemy.speed = 0
                enemy.state = "attacking"
                target.take_damage(0.05)  # IDamageable.take_damage()
            else:
                enemy.state = "walking"
                enemy.update()            # IMovable.update()

    # ── Colisiones (LSP: opera sobre IDamageable) ──────────────────── #

    def _check_collisions(self) -> None:
        """
        Detecta colisiones proyectil → enemigo.
        LSP: llama take_damage() sobre cualquier IDamageable.
        """
        for proj in self.projectiles:
            if not proj.active:
                continue
            for enemy in self.enemies:
                if not enemy.is_alive or proj.team == enemy.team:
                    continue

                if proj.collides_with(enemy.x, enemy.y, 40, 40):
                    killed = enemy.take_damage(proj.damage)
                    proj.deactivate()
                    if killed:
                        killer = self.players.get(proj.owner_name)
                        if killer:
                            killer.add_score(20)
                        self._emit(EVENT_ENEMY_KILLED, {
                            "enemy": enemy,
                            "killer": proj.owner_name
                        })

    # ── Condiciones de fin de juego ────────────────────────────────── #

    def _check_game_over(self) -> None:
        """
        Verifica las dos condiciones de victoria:
          1. Un castillo llega a 0 HP → gana el otro equipo.
          2. Se acaba el tiempo → gana quien tenga más puntos.
        """
        # Condición 1: castillo destruido
        for team, castle in self.castles.items():
            if castle.hp <= 0:
                self.running = False
                self.winner_team = "B" if team == "A" else "A"
                self._emit(EVENT_GAME_OVER, {"winner_team": self.winner_team})
                return

        # Condición 2: tiempo agotado
        if self.remaining_time <= 0:
            self.running = False
            score_a = sum(p.score for p in self.players.values() if p.team == "A")
            score_b = sum(p.score for p in self.players.values() if p.team == "B")
            self.winner_team = "A" if score_a > score_b else "B"
            self._emit(EVENT_GAME_OVER, {"winner_team": self.winner_team})

    # ── Tiempo ─────────────────────────────────────────────────────── #

    @property
    def remaining_time(self) -> float:
        """Segundos que quedan antes del fin del juego por tiempo."""
        return max(0.0, self.game_duration - (time.time() - self._start_time))

    # ── Serialización ──────────────────────────────────────────────── #

    def to_dict(self) -> dict:
        """
        Serializa el estado completo para enviarlo por UDP.
        ISP: incluye solo los datos que la red necesita.
        """
        return {
            "players": [p.to_dict() for p in self.players.values()],
            "enemies": [
                {
                    "id": e.id, "x": e.x, "y": e.y, "team": e.team,
                    "type": e.type, "hp": e.hp, "state": e.state
                } for e in self.enemies
            ],
            "castles":        {t: {"hp": c.hp} for t, c in self.castles.items()},
            "remaining_time": self.remaining_time,
            "running":        self.running,
            "winner":         self.winner_team
        }