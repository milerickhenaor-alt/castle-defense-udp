from __future__ import annotations
import time
import random # Necesario para la variación en Y
from typing import Callable, Dict, List, Optional

from model.castle      import Castle
from model.enemy       import Enemy
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
    Núcleo de la lógica del juego. Gestiona entidades, colisiones y eventos.
    Implementa Singleton para asegurar una única fuente de verdad.
    """

    _instance: Optional[GameState] = None

    @classmethod
    def get_instance(cls) -> "GameState":
        if cls._instance is None:
            raise RuntimeError("GameState no inicializado. Crea la instancia primero.")
        return cls._instance

    def __init__(
        self,
        players: List[Player],
        castles: Dict[str, Castle],
        map_width: int          = 1280,
        map_height: int         = 720,
        enemy_spawn_interval: float = 12.0, # 🔥 Intervalo más relajado
        game_duration: float    = 180.0,
        wave_scaling: bool      = True,
    ) -> None:
        GameState._instance = self

        # Entidades
        self.players:     Dict[str, Player] = {p.name: p for p in players}
        self.castles:     Dict[str, Castle] = castles
        self.enemies:     List[Enemy]       = []
        self.projectiles: List[Projectile]  = []

        # Configuración
        self.map_width  = map_width
        self.map_height = map_height
        self._start_time:      float = time.time()
        self._last_spawn_time: float = 0 # 0 para que el primer spawn sea inmediato
        self.enemy_spawn_interval    = enemy_spawn_interval
        self.max_enemies_on_screen   = 4 # 🔥 Límite para que no salgan tantos
        self.game_duration           = game_duration

        self._wave_number: int   = 0
        self._wave_scaling: bool = wave_scaling
        self.running:      bool  = True
        self.winner_team:  str   = ""

        # Observer
        self._listeners: Dict[str, List[Callable]] = {
            event: [] for event in _ALL_EVENTS
        }

    # ── Observer API ──────────────────────────────────────────────────── #

    def subscribe(self, event: str, callback: Callable) -> None:
        if event in self._listeners:
            self._listeners[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        if event in self._listeners:
            self._listeners[event] = [
                cb for cb in self._listeners[event] if cb is not callback
            ]

    def _emit(self, event: str, payload: dict) -> None:
        for cb in self._listeners.get(event, []):
            cb(payload)

    @property
    def elapsed_time(self) -> float:
        return time.time() - self._start_time

    @property
    def remaining_time(self) -> float:
        return max(0.0, self.game_duration - self.elapsed_time)

    # ── Update principal ───────────────────────────────────────────── #

    def update(self) -> None:
        if not self.running:
            return

        self._spawn_enemies()
        self._update_movables() 
        self._check_collisions()
        self._check_game_over()

    # ── Lógica de Spawn Corregida Definitivamente ────────────────── #

    def _spawn_enemies(self) -> None:
        now = time.time()
        if now - self._last_spawn_time < self.enemy_spawn_interval or len(self.enemies) >= self.max_enemies_on_screen:
            return

        self._last_spawn_time = now
        
        # --- RANGO DE CAMINO (Eje Y) ---
        # Según tus líneas, el camino está entre la parte media y baja.
        # Ajustamos para que salgan en ese "pasillo" verde.
        spawn_y = random.randint(350, 450) 

        # --- PUNTOS DE SALIDA (X) ---
        # Ajustado para que salgan justo donde terminan tus líneas negras cerca de los castillos
        PUNTO_SALIDA_IZQUIERDA = 177  # Fin de la línea negra del Castillo A
        PUNTO_SALIDA_DERECHA = 832  # Inicio de la línea negra del Castillo B (ajustado a un mapa de ~1200)

        try:
            self.enemies.append(EnemyFactory.create("A", PUNTO_SALIDA_IZQUIERDA, spawn_y, "normal"))
            self.enemies.append(EnemyFactory.create("B", PUNTO_SALIDA_DERECHA, spawn_y, "normal"))
        except Exception as e:
            print(f"Error: {e}")

    def _update_movables(self) -> None:
        # --- LÍMITES DE ATAQUE (X) ---
        MURO_DERECHO = 832   # El equipo A se detiene aquí
        MURO_IZQUIERDO = 177  # El equipo B se detiene aquí
        
        alive_enemies = []
        for enemy in self.enemies:
            if not enemy.is_alive or not enemy.active:
                continue

            if enemy.team == "A":
                llegó = enemy.x >= MURO_DERECHO
                target_team = "B" # 🔥 Definimos el equipo objetivo
                target_castle = self.castles["B"]
            else:
                llegó = enemy.x <= MURO_IZQUIERDO
                target_team = "A" # 🔥 Definimos el equipo objetivo
                target_castle = self.castles["A"]

            if llegó:
                enemy.speed = 0
                enemy.state = "attacking"
                
                # Aplicamos el daño al objeto castillo
                # 0.05 es un buen valor para que baje visiblemente pero no instantáneo
                target_castle.take_damage(enemy.damage * 0.01) 
                
                # Notificamos al HUD
                self._emit(EVENT_CASTLE_DAMAGED, {
                    "castle": target_castle,
                    "team": target_team,
                    "current_hp": target_castle.hp,
                    "max_hp": target_castle.max_hp
                })
            else:
                enemy.state = "walking"
                enemy.update()

            alive_enemies.append(enemy)
        self.enemies = alive_enemies

    # ── Colisiones y Fin (Resto igual) ───────────────────────────── #

    def _check_collisions(self) -> None:
        for proj in self.projectiles:
            if not proj.active: continue
            for enemy in self.enemies:
                if not enemy.is_alive or proj.team == enemy.team:
                    continue 
                if proj.collides_with(enemy.x, enemy.y, enemy.width, enemy.height):
                    self._emit(EVENT_PROJECTILE_HIT, {"projectile": proj, "enemy": enemy})
                    killed = enemy.take_damage(proj.damage)
                    proj.deactivate()
                    if killed:
                        self._on_enemy_killed(enemy, proj.owner_name)
                    break

    def _on_enemy_killed(self, enemy: Enemy, killer_name: str) -> None:
        player = self.players.get(killer_name)
        if player:
            player.add_score(enemy.reward)
        self._emit(EVENT_ENEMY_KILLED, {"enemy": enemy, "killer": killer_name})

    def _check_game_over(self) -> None:
        if not self.running: return

        # Por destrucción de castillo
        for team, castle in self.castles.items():
            if castle.is_destroyed:
                winner = "B" if team == "A" else "A"
                self._end_game(winner)
                return

        # Por tiempo
        if self.remaining_time <= 0:
            score_a = sum(p.score for p in self.players.values() if p.team == "A")
            score_b = sum(p.score for p in self.players.values() if p.team == "B")
            if score_a > score_b: self._end_game("A")
            elif score_b > score_a: self._end_game("B")
            else: self._end_game("draw")

    def _end_game(self, winner_team: str) -> None:
        self.running = False
        self.winner_team = winner_team
        self._emit(EVENT_GAME_OVER, {"winner_team": winner_team})

    # ── Utilidades de Red ─────────────────────────────────────────── #

    def add_projectile(self, proj: Projectile) -> None:
        self.projectiles.append(proj)

    def add_enemy(self, enemy: Enemy) -> None:
        # Importante: Asegurar que el ID no se duplique al recibir de red
        for existing in self.enemies:
            if existing.id == enemy.id:
                return # Ya lo tenemos
        self.enemies.append(enemy)

    def update_player_from_network(self, data: dict) -> None:
        name = data.get("name")
        if name and name in self.players:
            self.players[name].set_position(data["x"], data["y"])
            self.players[name].score = data.get("score", self.players[name].score)

    def to_dict(self) -> dict:
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