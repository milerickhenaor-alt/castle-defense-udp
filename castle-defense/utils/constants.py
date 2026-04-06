# =========================
# 🎮 SCREEN CONFIG
# =========================
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60


# =========================
# 🎨 COLORS (RGB)
# =========================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (150, 150, 150)


# =========================
# 🧍 PLAYER CONFIG
# =========================
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5
PLAYER_COOLDOWN = 0.5  # segundos entre disparos


# =========================
# 🏹 PROJECTILES
# =========================
PROJECTILE_WIDTH = 10
PROJECTILE_HEIGHT = 10
PROJECTILE_SPEED = 8
PROJECTILE_DAMAGE = 25


# =========================
# 👹 ENEMY (TROLL)
# =========================
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 40
ENEMY_SPEED = 2
ENEMY_HEALTH = 100
ENEMY_DAMAGE = 20
ENEMY_SPAWN_INTERVAL = 3  # segundos


# =========================
# 🏰 CASTLE
# =========================
CASTLE_WIDTH = 80
CASTLE_HEIGHT = 120
CASTLE_MAX_HEALTH = 1000


# =========================
# 🎯 GAME RULES
# =========================
GAME_DURATION = 120  # segundos
POINTS_PER_ENEMY = 10


# =========================
# 📊 HUD
# =========================
FONT_NAME = "Arial"
FONT_SMALL = 20
FONT_MEDIUM = 28
FONT_LARGE = 40


# =========================
# 🎬 ANIMATIONS
# =========================
ANIMATION_SPEED = 0.15  # velocidad de animación


# =========================
# 📡 NETWORK (UDP)
# =========================
SERVER_IP = "127.0.0.1"   # cambiar por IP real
SERVER_PORT = 5000
BUFFER_SIZE = 65535


# =========================
# 🎮 PLAYER STATES
# =========================
STATE_IDLE = "idle"
STATE_WALK = "walk"
STATE_ATTACK = "attack"


# =========================
# 👹 ENEMY STATES
# =========================
ENEMY_STATE_WALK = "walk"
ENEMY_STATE_HIT = "hit"
ENEMY_STATE_DEATH = "death"
ENEMY_STATE_ATTACK = "attack"


# =========================
# 🏰 CASTLE STATES
# =========================
CASTLE_FULL = "full"
CASTLE_DAMAGED = "damaged"
CASTLE_DESTROYED = "destroyed"