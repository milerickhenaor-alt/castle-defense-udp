"""
model/game_state.py
Persona 1 — Model Core

Motor de reglas del juego.

Patrones de diseño aplicados
-----------------------------
1. Observer (Publicador/Suscriptor)
   ¿Por qué?
       El modelo (GameState) necesita notificar eventos a otras capas
       (controller, red, sonido) sin depender de ellas directamente.
       Si GameState llamara directamente a network.send() o sound.play(),
       violaría DIP y acoplaría el modelo a la infraestructura.
   ¿Cómo?
       GameState mantiene un dict de listas de callbacks por evento.
       Cualquier módulo externo se suscribe con subscribe(evento, fn).
       Cuando ocurre el evento, GameState llama a todos los callbacks
       registrados pasándoles un payload con los datos relevantes.
   Eventos disponibles:
       EVENT_ENEMY_KILLED    → payload: {"enemy": Enemy, "killer": str}
       EVENT_CASTLE_DAMAGED  → payload: {"castle": Castle, "damage": int}
       EVENT_GAME_OVER       → payload: {"winner_team": str}
       EVENT_PROJECTILE_HIT  → payload: {"projectile": Projectile, "enemy": Enemy}

2. Singleton
   ¿Por qué?
       Solo puede existir un estado de juego por proceso. Si el controller
       y la red crearan instancias distintas, habría dos fuentes de verdad
       inconsistentes.
   ¿Cómo?
       GameState guarda su instancia en _instance. El constructor la asigna
       al crearse. GameState.get_instance() la devuelve desde cualquier módulo.

3. Factory Method (en factories.py)
   GameState delega la creación de enemies a EnemyFactory, no los construye
   directamente. Esto cumple OCP: cambiar cómo se generan los enemigos no
   modifica GameState.

Principios SOLID
----------------
SRP : GameState solo ejecuta la lógica del juego. Sin pygame, sin sockets.
OCP : Nuevos eventos se agregan al dict sin tocar el núcleo.
LSP : Opera sobre IDamageable e IMovable; no asume tipos concretos.
ISP : Consume solo las interfaces que necesita de cada entidad.
DIP : Depende de abstracciones (interfaces), no de clases concretas.
"""

from __future__ import annotations

import time
from typing import Callable, Dict, List, Optional

from model.castle      import Castle
from model.enemy       import Enemy
from model.interfaces  import IDamageable, IMovable
from model.player      import Player
from model.projectile  import Projectile
from model.factories   import EnemyFactory


# ─────────────────────────────────────────────────────────────────────────────
# Constantes de eventos del Observer
# ─────────────────────────────────────────────────────────────────────────────

EVENT_ENEMY_KILLED    = "enemy_killed"
EVENT_CASTLE_DAMAGED  = "castle_damaged"
EVENT_GAME_OVER       = "game_over"
EVENT_PROJECTILE_HIT  = "projectile_hit"

_ALL_EVENTS = (
    EVENT_ENEMY_KILLED,
    EVENT_CASTLE_DAMAGED,
    EVENT_GAME_OVER,
    EVENT_PROJECTILE_HIT,
)


# ─────────────────────────────────────────────────────────────────────────────
# GameState — Singleton + Observer
# ─────────────────────────────────────────────────────────────────────────────

class GameState:
    """
    Núcleo de la lógica del juego.

    Gestiona y actualiza:
      • jugadores  (players)
      • castillos  (castles)
      • enemigos   (enemies)
      • proyectiles (projectiles)
      • puntajes, tiempo, estado de partida

    Sin ninguna dependencia de pygame, sockets o interfaz gráfica.
    """

    # ── Singleton ─────────────────────────────────────────────────────── #
    _instance: Optional[GameState] = None

    @classmethod
    def get_instance(cls) -> "GameState":
        """
        [Singleton] Devuelve la instancia única del estado del juego.
        Lanza RuntimeError si aún no ha sido creada.
        """
        if cls._instance is None:
            raise RuntimeError(
                "GameState no ha sido inicializado. "
                "Crea una instancia con GameState(...) primero."
            )
        return cls._instance

    # ── Constructor ───────────────────────────────────────────────────── #

    def __init__(
        self,
        players: List[Player],
        castles: Dict[str, Castle],    # {"A": Castle, "B": Castle}
        map_width: int          = 1280,
        map_height: int         = 720,
        enemy_spawn_interval: float = 3.0,
        game_duration: float    = 180.0,
        wave_scaling: bool      = True,
    ) -> None:
        # Singleton: registrar esta instancia
        GameState._instance = self

        # Entidades del juego
        self.players:     Dict[str, Player]     = {p.name: p for p in players}
        self.castles:     Dict[str, Castle]     = castles
        self.enemies:     List[Enemy]           = []
        self.projectiles: List[Projectile]      = []

        # Configuración del mapa
        self.map_width  = map_width
        self.map_height = map_height

        # Configuración temporal
        self._start_time:       float = time.time()
        self._last_spawn_time:  float = time.time()
        self.enemy_spawn_interval     = enemy_spawn_interval
        self.game_duration            = game_duration

        # Escalado de oleadas
        self._wave_number: int   = 0
        self._wave_scaling: bool = wave_scaling

        # Estado de la partida
        self.running:      bool = True
        self.winner_team:  str  = ""

        # ── Observer: registro de listeners ────────────────────────── #
        self._listeners: Dict[str, List[Callable]] = {
            event: [] for event in _ALL_EVENTS
        }

    # ── Observer — API pública ─────────────────────────────────────── #

    def subscribe(self, event: str, callback: Callable) -> None:
        """
        [Observer] Registra un listener para el evento indicado.

        Ejemplo de uso desde el controller (Persona 3):
            state.subscribe(EVENT_GAME_OVER, view.show_end_screen)

        Ejemplo de uso desde la red (Persona 4):
            state.subscribe(EVENT_ENEMY_KILLED, network.broadcast_kill)
        """
        if event in self._listeners:
            self._listeners[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        """[Observer] Elimina un listener previamente registrado."""
        if event in self._listeners:
            self._listeners[event] = [
                cb for cb in self._listeners[event] if cb is not callback
            ]

    def _emit(self, event: str, payload: dict) -> None:
        """
        [Observer] Notifica a todos los suscriptores de un evento.
        Interno: solo GameState lo llama.
        """
        for cb in self._listeners.get(event, []):
            cb(payload)

    # ── Propiedades de tiempo ──────────────────────────────────────── #

    @property
    def elapsed_time(self) -> float:
        """Segundos transcurridos desde el inicio de la partida."""
        return time.time() - self._start_time

    @property
    def remaining_time(self) -> float:
        """Segundos que quedan antes del fin por tiempo."""
        return max(0.0, self.game_duration - self.elapsed_time)

    # ── Update principal ───────────────────────────────────────────── #

    def update(self) -> None:
        """
        Ejecuta un ciclo completo de lógica del juego.
        Debe llamarse 60 veces por segundo desde el game loop (Persona 3).

        Orden del ciclo (según el documento base del equipo):
          1. Generar enemigos
          2. Mover enemigos
          3. Mover proyectiles
          4. Detectar colisiones
          5. Verificar condiciones de fin
        """
        if not self.running:
            return

        self._spawn_enemies()
        self._update_movables()   # LSP: Enemy y Projectile como IMovable
        self._check_collisions()
        self._check_game_over()

    # ── Generación de enemigos (Factory Method) ────────────────────── #

    def _spawn_enemies(self) -> None:
        """
        Genera una oleada de trolls si pasó el intervalo de spawn.

        Delega la construcción a EnemyFactory (patrón Factory Method).
        OCP: cambiar tipos o cantidades de enemies no modifica este método.
        """
        now = time.time()
        if now - self._last_spawn_time < self.enemy_spawn_interval:
            return

        self._last_spawn_time = now
        self._wave_number += 1

        castle_a = self.castles["A"]
        castle_b = self.castles["B"]
        mid_y    = self.map_height / 2

        wave = self._wave_number if self._wave_scaling else 1

        # Oleada del equipo A: nace junto al castillo A, avanza hacia B
        for enemy in EnemyFactory.create_wave("A", castle_a.x + castle_a.width, mid_y, wave):
            self.enemies.append(enemy)

        # Oleada del equipo B: nace junto al castillo B, avanza hacia A
        for enemy in EnemyFactory.create_wave("B", castle_b.x, mid_y, wave):
            self.enemies.append(enemy)

    # ── Movimiento (LSP: opera sobre IMovable) ─────────────────────── #

    def _update_movables(self) -> None:
        """
        Llama update() sobre todos los IMovable activos (Enemy y Projectile).

        LSP en acción: este método no distingue entre Enemy y Projectile.
        Cualquier clase que implemente IMovable funciona aquí.
        """
        # Enemigos
        alive_enemies = []
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            enemy.update()   # IMovable.update()

            target_team   = "B" if enemy.team == "A" else "A"
            target_castle = self.castles[target_team]

            if enemy.has_reached_castle(target_castle.x, target_castle.width):
                target_castle.take_damage(enemy.damage)   # IDamageable.take_damage()
                enemy.active = False
                self._emit(EVENT_CASTLE_DAMAGED, {
                    "castle": target_castle,
                    "damage": enemy.damage,
                })
            else:
                alive_enemies.append(enemy)

        self.enemies = alive_enemies

        # Proyectiles
        active_projs = []
        for proj in self.projectiles:
            if not proj.active:
                continue
            proj.update()   # IMovable.update()
            if proj.is_out_of_bounds(self.map_width, self.map_height):
                proj.deactivate()
            else:
                active_projs.append(proj)

        self.projectiles = active_projs

    # ── Detección de colisiones ────────────────────────────────────── #

    def _check_collisions(self) -> None:
        """
        Proyectil vs Enemigo (AABB).

        Regla: un proyectil solo daña a enemigos del equipo contrario.
        Un proyectil impacta a un solo enemigo por frame y desaparece.
        """
        for proj in self.projectiles:
            if not proj.active:
                continue
            for enemy in self.enemies:
                if not enemy.is_alive:
                    continue
                if proj.team == enemy.team:
                    continue   # No daña a aliados
                if proj.collides_with(enemy.x, enemy.y, enemy.width, enemy.height):
                    self._emit(EVENT_PROJECTILE_HIT, {"projectile": proj, "enemy": enemy})
                    killed = enemy.take_damage(proj.damage)   # IDamageable
                    proj.deactivate()
                    if killed:
                        self._on_enemy_killed(enemy, proj.owner_name)
                    break

    def _on_enemy_killed(self, enemy: Enemy, killer_name: str) -> None:
        """
        Asigna puntos al jugador que mató al enemigo y emite el evento Observer.
        El controller y la red se enteran mediante su suscripción al evento.
        """
        player = self.players.get(killer_name)
        if player:
            player.add_score(enemy.reward)
        self._emit(EVENT_ENEMY_KILLED, {"enemy": enemy, "killer": killer_name})

    # ── Condiciones de fin de juego ────────────────────────────────── #

    def _check_game_over(self) -> None:
        """
        Verifica las dos condiciones de victoria definidas en el documento:
          1. Un castillo llega a 0 de vida → gana el otro equipo.
          2. Se acaba el tiempo → gana quien tenga más puntos (o empate).
        """
        if not self.running:
            return

        # Condición 1: castillo destruido
        for team, castle in self.castles.items():
            if castle.is_destroyed:
                winner = "B" if team == "A" else "A"
                self._end_game(winner)
                return

        # Condición 2: tiempo agotado
        if self.remaining_time <= 0:
            score_a = sum(p.score for p in self.players.values() if p.team == "A")
            score_b = sum(p.score for p in self.players.values() if p.team == "B")
            if score_a > score_b:
                self._end_game("A")
            elif score_b > score_a:
                self._end_game("B")
            else:
                self._end_game("draw")

    def _end_game(self, winner_team: str) -> None:
        """Detiene el juego y notifica a todos los suscriptores de EVENT_GAME_OVER."""
        self.running     = False
        self.winner_team = winner_team
        self._emit(EVENT_GAME_OVER, {"winner_team": winner_team})

    # ── API pública para el controller y la red ────────────────────── #

    def add_projectile(self, proj: Projectile) -> None:
        """
        Agrega un proyectil al estado.
        Llamado por el controller (Persona 3) cuando un jugador dispara.
        """
        self.projectiles.append(proj)

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Agrega un enemigo recibido por red.
        Llamado por la capa UDP (Persona 4) para sincronizar enemigos remotos.
        """
        self.enemies.append(enemy)

    def update_player_from_network(self, data: dict) -> None:
        """
        Actualiza la posición de un jugador recibida por UDP.
        Llamado por la capa de red (Persona 4).
        """
        name = data.get("name")
        if name and name in self.players:
            self.players[name].set_position(data["x"], data["y"])
            self.players[name].score = data.get("score", self.players[name].score)

    def apply_castle_damage_from_network(self, team: str, damage: int) -> None:
        """
        Aplica daño a un castillo a partir de un evento recibido por red.
        Evita duplicar la lógica de daño en la capa de red.
        """
        castle = self.castles.get(team)
        if castle:
            castle.take_damage(damage)

    # ── Serialización del estado completo ─────────────────────────── #

    def to_dict(self) -> dict:
        """
        Snapshot completo del estado, serializable en JSON para UDP.
        La capa de red (Persona 4) llama esto para construir el paquete.
        """
        return {
            "players":     [p.to_dict() for p in self.players.values()],
            "castles":     {t: c.to_dict() for t, c in self.castles.items()},
            "enemies":     [e.to_dict() for e in self.enemies],
            "projectiles": [p.to_dict() for p in self.projectiles],
            "elapsed":     self.elapsed_time,
            "running":     self.running,
            "winner":      self.winner_team,
            "wave":        self._wave_number,
        }

    def __repr__(self) -> str:
        return (
            f"GameState(running={self.running}, wave={self._wave_number}, "
            f"players={list(self.players.keys())}, "
            f"enemies={len(self.enemies)}, "
            f"projectiles={len(self.projectiles)})"
        )