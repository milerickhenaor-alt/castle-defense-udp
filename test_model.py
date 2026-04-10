"""
test_model.py
Persona 1 — Model Core

Tests unitarios para verificar el comportamiento de todas las clases del modelo.

¿Por qué tests?
---------------
Durante la sustentación individual, la profesora puede pedir demostrar
que el código funciona correctamente. Ejecutar estos tests en vivo muestra
dominio técnico y confianza en el código propio.

Cómo ejecutar:
    python -m pytest test_model.py -v
    o
    python test_model.py

No requiere pygame ni conexión de red. El modelo es puro Python.
"""

import sys
import time
import unittest

# ── Asegura que Python encuentre el paquete model ─────────────────────────
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_players():
    """Crea dos jugadores de prueba, uno por equipo."""
    return [
        Player(name="Alice", team="A", x=100.0, y=360.0),
        Player(name="Bob",   team="B", x=1180.0, y=360.0),
    ]

def make_castles():
    """Crea los dos castillos en los extremos del mapa."""
    return {
        "A": Castle(team="A", x=0.0,    y=296.0, max_hp=1000, hp=1000),
        "B": Castle(team="B", x=1216.0, y=296.0, max_hp=1000, hp=1000),
    }

def make_game_state():
    """Crea un GameState limpio para cada test."""
    # Resetear Singleton entre tests
    GameState._instance = None
    return GameState(
        players=make_players(),
        castles=make_castles(),
        map_width=1280,
        map_height=720,
        enemy_spawn_interval=999.0,  # Desactivar spawn automático en tests
        game_duration=180.0,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Player
# ─────────────────────────────────────────────────────────────────────────────

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player(name="Alice", team="A", x=100.0, y=100.0)

    def test_movimiento_normal(self):
        """El jugador se mueve correctamente en x e y."""
        self.player.move(1, 0, 1280, 720)
        self.assertAlmostEqual(self.player.x, 105.0)  # speed=5
        self.player.move(0, 1, 1280, 720)
        self.assertAlmostEqual(self.player.y, 105.0)

    def test_movimiento_limitado_bordes(self):
        """El jugador no puede salir del mapa."""
        self.player.move(-100, -100, 1280, 720)
        self.assertEqual(self.player.x, 0.0)
        self.assertEqual(self.player.y, 0.0)

        self.player.set_position(1200.0, 700.0)
        self.player.move(100, 100, 1280, 720)
        self.assertEqual(self.player.x, 1279.0)
        self.assertEqual(self.player.y, 719.0)

    def test_puntaje_suma_correctamente(self):
        """add_score solo acepta valores positivos."""
        self.player.add_score(10)
        self.assertEqual(self.player.score, 10)
        self.player.add_score(-5)   # No debe restar
        self.assertEqual(self.player.score, 10)
        self.player.add_score(0)    # No debe sumar
        self.assertEqual(self.player.score, 10)

    def test_disparo_crea_proyectil(self):
        """shoot() devuelve un Projectile si el cooldown lo permite."""
        self.player.shoot_cooldown = 0.0   # Sin cooldown para el test
        proj = self.player.shoot((1.0, 0.0))
        self.assertIsNotNone(proj)
        self.assertEqual(proj.owner_name, "Alice")
        self.assertEqual(proj.team, "A")

    def test_disparo_en_cooldown_retorna_none(self):
        """shoot() devuelve None si no pasó el cooldown."""
        self.player.shoot_cooldown = 999.0
        self.player._last_shot_time = time.time()
        proj = self.player.shoot((1.0, 0.0))
        self.assertIsNone(proj)

    def test_serializacion_ida_y_vuelta(self):
        """to_dict() y from_dict() son inversas entre sí."""
        self.player.score = 42
        data   = self.player.to_dict()
        copia  = Player.from_dict(data)
        self.assertEqual(copia.name,  self.player.name)
        self.assertEqual(copia.team,  self.player.team)
        self.assertEqual(copia.x,     self.player.x)
        self.assertEqual(copia.score, self.player.score)


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Enemy
# ─────────────────────────────────────────────────────────────────────────────

class TestEnemy(unittest.TestCase):

    def test_movimiento_equipo_a_avanza_derecha(self):
        """Enemigo del equipo A avanza hacia la derecha (+x)."""
        enemy = Enemy(team="A", x=100.0, y=360.0, speed=2.0)
        enemy.update()
        self.assertAlmostEqual(enemy.x, 102.0)

    def test_movimiento_equipo_b_avanza_izquierda(self):
        """Enemigo del equipo B avanza hacia la izquierda (-x)."""
        enemy = Enemy(team="B", x=900.0, y=360.0, speed=2.0)
        enemy.update()
        self.assertAlmostEqual(enemy.x, 898.0)

    def test_daño_reduce_vida(self):
        """take_damage reduce hp correctamente."""
        enemy = Enemy(team="A", x=0.0, y=0.0, hp=100)
        enemy.take_damage(30)
        self.assertEqual(enemy.hp, 70)

    def test_daño_letal_mata_enemigo(self):
        """take_damage devuelve True y desactiva al enemigo cuando hp llega a 0."""
        enemy = Enemy(team="A", x=0.0, y=0.0, hp=50)
        killed = enemy.take_damage(50)
        self.assertTrue(killed)
        self.assertFalse(enemy.is_alive)
        self.assertFalse(enemy.active)

    def test_daño_no_baja_de_cero(self):
        """hp nunca es negativo."""
        enemy = Enemy(team="A", x=0.0, y=0.0, hp=10)
        enemy.take_damage(999)
        self.assertEqual(enemy.hp, 0)

    def test_hp_ratio(self):
        """hp_ratio refleja correctamente la fracción de vida."""
        enemy = Enemy(team="A", x=0.0, y=0.0, hp=50, max_hp=100)
        self.assertAlmostEqual(enemy.hp_ratio, 0.5)

    def test_llega_al_castillo(self):
        """has_reached_castle detecta correctamente el contacto con el castillo."""
        # Equipo A llega al castillo B (en x=1216)
        enemy = Enemy(team="A", x=1200.0, y=360.0, width=32.0)
        self.assertTrue(enemy.has_reached_castle(castle_x=1216.0, castle_width=64.0))

    def test_serializacion_ida_y_vuelta(self):
        """to_dict() y from_dict() son inversas."""
        enemy = Enemy(team="B", x=500.0, y=300.0, hp=80, speed=2.0)
        copia = Enemy.from_dict(enemy.to_dict())
        self.assertEqual(copia.team,  enemy.team)
        self.assertEqual(copia.hp,    enemy.hp)
        self.assertEqual(copia.speed, enemy.speed)
        self.assertEqual(copia.id,    enemy.id)


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Castle
# ─────────────────────────────────────────────────────────────────────────────

class TestCastle(unittest.TestCase):

    def setUp(self):
        self.castle = Castle(team="A", x=0.0, y=296.0, max_hp=1000, hp=1000)

    def test_daño_reduce_vida(self):
        """take_damage reduce hp del castillo correctamente."""
        self.castle.take_damage(200)
        self.assertEqual(self.castle.hp, 800)

    def test_castillo_no_queda_en_negativo(self):
        """hp nunca baja de 0."""
        self.castle.take_damage(9999)
        self.assertEqual(self.castle.hp, 0)

    def test_is_destroyed_cuando_hp_es_cero(self):
        """is_destroyed es True cuando el castillo cae."""
        self.castle.take_damage(1000)
        self.assertTrue(self.castle.is_destroyed)

    def test_no_destruido_con_vida_restante(self):
        """is_destroyed es False mientras quede vida."""
        self.castle.take_damage(999)
        self.assertFalse(self.castle.is_destroyed)

    def test_hp_ratio(self):
        """hp_ratio refleja correctamente la fracción de vida."""
        self.castle.take_damage(500)
        self.assertAlmostEqual(self.castle.hp_ratio, 0.5)

    def test_serializacion_ida_y_vuelta(self):
        """to_dict() y from_dict() son inversas."""
        self.castle.take_damage(300)
        copia = Castle.from_dict(self.castle.to_dict())
        self.assertEqual(copia.team,   self.castle.team)
        self.assertEqual(copia.hp,     self.castle.hp)
        self.assertEqual(copia.max_hp, self.castle.max_hp)


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Projectile
# ─────────────────────────────────────────────────────────────────────────────

class TestProjectile(unittest.TestCase):

    def test_avanza_en_direccion_correcta(self):
        """update() mueve el proyectil según dx/dy y speed."""
        proj = Projectile(owner_name="Alice", team="A",
                          x=100.0, y=100.0, dx=1.0, dy=0.0, speed=10.0)
        proj.update()
        self.assertAlmostEqual(proj.x, 110.0)
        self.assertAlmostEqual(proj.y, 100.0)

    def test_fuera_de_bordes(self):
        """is_out_of_bounds detecta cuando el proyectil sale del mapa."""
        proj = Projectile(owner_name="Alice", team="A",
                          x=-1.0, y=100.0, dx=1.0, dy=0.0)
        self.assertTrue(proj.is_out_of_bounds(1280, 720))

    def test_dentro_de_bordes(self):
        """is_out_of_bounds devuelve False cuando está dentro del mapa."""
        proj = Projectile(owner_name="Alice", team="A",
                          x=640.0, y=360.0, dx=1.0, dy=0.0)
        self.assertFalse(proj.is_out_of_bounds(1280, 720))

    def test_colision_dentro_del_objetivo(self):
        """collides_with devuelve True si el proyectil está dentro del rect."""
        proj = Projectile(owner_name="Alice", team="A",
                          x=50.0, y=50.0, dx=1.0, dy=0.0)
        self.assertTrue(proj.collides_with(40.0, 40.0, 32.0, 32.0))

    def test_sin_colision_fuera_del_objetivo(self):
        """collides_with devuelve False si el proyectil está fuera del rect."""
        proj = Projectile(owner_name="Alice", team="A",
                          x=200.0, y=200.0, dx=1.0, dy=0.0)
        self.assertFalse(proj.collides_with(40.0, 40.0, 32.0, 32.0))

    def test_deactivate(self):
        """deactivate() marca el proyectil como inactivo."""
        proj = Projectile(owner_name="Alice", team="A",
                          x=100.0, y=100.0, dx=1.0, dy=0.0)
        self.assertTrue(proj.active)
        proj.deactivate()
        self.assertFalse(proj.active)

    def test_serializacion_ida_y_vuelta(self):
        """to_dict() y from_dict() son inversas."""
        proj  = Projectile(owner_name="Bob", team="B",
                           x=300.0, y=200.0, dx=-1.0, dy=0.0, damage=60)
        copia = Projectile.from_dict(proj.to_dict())
        self.assertEqual(copia.owner_name, proj.owner_name)
        self.assertEqual(copia.damage,     proj.damage)
        self.assertEqual(copia.id,         proj.id)


# ─────────────────────────────────────────────────────────────────────────────
# Tests: EnemyFactory
# ─────────────────────────────────────────────────────────────────────────────

class TestEnemyFactory(unittest.TestCase):

    def test_crea_enemigo_normal(self):
        """EnemyFactory.create() produce un Enemy del tipo normal."""
        enemy = EnemyFactory.create("A", 100.0, 360.0, "normal")
        self.assertIsInstance(enemy, Enemy)
        self.assertEqual(enemy.team, "A")
        self.assertEqual(enemy.hp, 100)

    def test_crea_enemigo_fast(self):
        """El tipo fast tiene más velocidad y menos vida que normal."""
        fast   = EnemyFactory.create("A", 0.0, 0.0, "fast")
        normal = EnemyFactory.create("A", 0.0, 0.0, "normal")
        self.assertGreater(fast.speed, normal.speed)
        self.assertLess(fast.hp, normal.hp)

    def test_crea_enemigo_tank(self):
        """El tipo tank tiene más vida y más daño que normal."""
        tank   = EnemyFactory.create("A", 0.0, 0.0, "tank")
        normal = EnemyFactory.create("A", 0.0, 0.0, "normal")
        self.assertGreater(tank.hp,     normal.hp)
        self.assertGreater(tank.damage, normal.damage)

    def test_tipo_invalido_lanza_error(self):
        """EnemyFactory.create() lanza ValueError con un tipo desconocido."""
        with self.assertRaises(ValueError):
            EnemyFactory.create("A", 0.0, 0.0, "gigante_jefe")

    def test_oleada_escala_con_wave(self):
        """create_wave genera más enemigos en oleadas avanzadas."""
        oleada_1 = EnemyFactory.create_wave("A", 0.0, 0.0, wave_number=1)
        oleada_4 = EnemyFactory.create_wave("A", 0.0, 0.0, wave_number=4)
        self.assertLess(len(oleada_1), len(oleada_4))


# ─────────────────────────────────────────────────────────────────────────────
# Tests: ProjectileFactory
# ─────────────────────────────────────────────────────────────────────────────

class TestProjectileFactory(unittest.TestCase):

    def test_crea_proyectil_basic(self):
        """ProjectileFactory.create() produce un Projectile del tipo basic."""
        proj = ProjectileFactory.create("Alice", "A", 100.0, 100.0, 1.0, 0.0, "basic")
        self.assertIsInstance(proj, Projectile)
        self.assertEqual(proj.owner_name, "Alice")

    def test_heavy_mas_daño_menos_velocidad(self):
        """heavy hace más daño pero viaja más lento que basic."""
        basic = ProjectileFactory.create("Alice", "A", 0.0, 0.0, 1.0, 0.0, "basic")
        heavy = ProjectileFactory.create("Alice", "A", 0.0, 0.0, 1.0, 0.0, "heavy")
        self.assertGreater(heavy.damage, basic.damage)
        self.assertLess(heavy.speed,    basic.speed)

    def test_tipo_invalido_lanza_error(self):
        """ProjectileFactory lanza ValueError con tipo desconocido."""
        with self.assertRaises(ValueError):
            ProjectileFactory.create("Alice", "A", 0.0, 0.0, 1.0, 0.0, "laser_nuclear")


# ─────────────────────────────────────────────────────────────────────────────
# Tests: GameState
# ─────────────────────────────────────────────────────────────────────────────

class TestGameState(unittest.TestCase):

    def setUp(self):
        self.state = make_game_state()

    def tearDown(self):
        GameState._instance = None

    def test_singleton_devuelve_misma_instancia(self):
        """GameState.get_instance() devuelve la instancia ya creada."""
        self.assertIs(GameState.get_instance(), self.state)

    def test_singleton_sin_instancia_lanza_error(self):
        """get_instance() lanza RuntimeError si no hay instancia."""
        GameState._instance = None
        with self.assertRaises(RuntimeError):
            GameState.get_instance()

    # ── Observer ────────────────────────────────────────────────────── #

    def test_observer_enemy_killed(self):
        """El evento enemy_killed se emite cuando un proyectil mata a un troll."""
        eventos = []
        self.state.subscribe(EVENT_ENEMY_KILLED, lambda p: eventos.append(p))

        # Colocar enemy vulnerable justo en la trayectoria del proyectil
        enemy = Enemy(team="B", x=200.0, y=200.0, hp=10, width=32.0, height=32.0)
        proj  = Projectile(owner_name="Alice", team="A",
                           x=200.0, y=200.0, dx=1.0, dy=0.0, damage=50)
        self.state.enemies.append(enemy)
        self.state.projectiles.append(proj)

        self.state._check_collisions()

        self.assertEqual(len(eventos), 1)
        self.assertEqual(eventos[0]["killer"], "Alice")

    def test_observer_castle_damaged(self):
        """El evento castle_damaged se emite cuando un troll llega al castillo."""
        eventos = []
        self.state.subscribe(EVENT_CASTLE_DAMAGED, lambda p: eventos.append(p))

        # Enemy del equipo A justo en el borde del castillo B
        castle_b = self.state.castles["B"]
        enemy = Enemy(team="A", x=castle_b.x - 1.0, y=360.0,
                      width=32.0, speed=2.0, damage=50)
        self.state.enemies.append(enemy)

        self.state._update_movables()

        self.assertEqual(len(eventos), 1)
        self.assertEqual(eventos[0]["damage"], 50)

    def test_observer_game_over_castillo_destruido(self):
        """El evento game_over se emite cuando un castillo cae a 0."""
        eventos = []
        self.state.subscribe(EVENT_GAME_OVER, lambda p: eventos.append(p))

        self.state.castles["A"].hp = 0
        self.state._check_game_over()

        self.assertEqual(len(eventos), 1)
        self.assertEqual(eventos[0]["winner_team"], "B")
        self.assertFalse(self.state.running)

    def test_observer_game_over_tiempo_agotado(self):
        """Al agotarse el tiempo gana quien tiene más puntos."""
        eventos = []
        self.state.subscribe(EVENT_GAME_OVER, lambda p: eventos.append(p))

        # Alice (equipo A) tiene más puntos
        self.state.players["Alice"].add_score(100)
        # Simular tiempo agotado
        self.state._start_time = time.time() - 999.0

        self.state._check_game_over()

        self.assertEqual(eventos[0]["winner_team"], "A")

    # ── Colisiones ──────────────────────────────────────────────────── #

    def test_proyectil_no_daña_aliados(self):
        """Un proyectil del equipo A no debe dañar a enemigos del equipo A."""
        enemy = Enemy(team="A", x=200.0, y=200.0, hp=100, width=32.0, height=32.0)
        proj  = Projectile(owner_name="Alice", team="A",
                           x=200.0, y=200.0, dx=1.0, dy=0.0, damage=50)
        self.state.enemies.append(enemy)
        self.state.projectiles.append(proj)

        self.state._check_collisions()

        self.assertEqual(enemy.hp, 100)   # Sin daño
        self.assertTrue(proj.active)      # Proyectil sigue activo

    def test_proyectil_se_desactiva_al_impactar(self):
        """El proyectil se desactiva después de golpear a un enemigo."""
        enemy = Enemy(team="B", x=200.0, y=200.0, hp=999, width=32.0, height=32.0)
        proj  = Projectile(owner_name="Alice", team="A",
                           x=200.0, y=200.0, dx=1.0, dy=0.0, damage=10)
        self.state.enemies.append(enemy)
        self.state.projectiles.append(proj)

        self.state._check_collisions()

        self.assertFalse(proj.active)

    # ── Puntaje ─────────────────────────────────────────────────────── #

    def test_puntos_se_asignan_al_matar_enemigo(self):
        """Matar un enemigo suma su reward al jugador correspondiente."""
        enemy = Enemy(team="B", x=200.0, y=200.0, hp=10,
                      width=32.0, height=32.0, reward=15)
        proj  = Projectile(owner_name="Alice", team="A",
                           x=200.0, y=200.0, dx=1.0, dy=0.0, damage=50)
        self.state.enemies.append(enemy)
        self.state.projectiles.append(proj)

        self.state._check_collisions()

        self.assertEqual(self.state.players["Alice"].score, 15)

    # ── Serialización del estado completo ───────────────────────────── #

    def test_to_dict_contiene_campos_esperados(self):
        """to_dict() incluye todos los campos necesarios para la red."""
        data = self.state.to_dict()
        for campo in ("players", "castles", "enemies", "projectiles",
                      "elapsed", "running", "winner", "wave"):
            self.assertIn(campo, data)


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Ejecutar con salida detallada
    loader  = unittest.TestLoader()
    suite   = loader.loadTestsFromModule(sys.modules[__name__])
    runner  = unittest.TextTestRunner(verbosity=2)
    result  = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)