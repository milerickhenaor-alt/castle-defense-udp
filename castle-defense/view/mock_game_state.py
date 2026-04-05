class DummyPlayer:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name
        self.health = 100


class DummyEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 50


class DummyCastle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 200


class DummyGameState:
    def __init__(self):
        self.players = [
            DummyPlayer(150, 300, "Player 1"),
            DummyPlayer(250, 300, "Player 2")
        ]

        self.enemies = [
            DummyEnemy(700, 300),
            DummyEnemy(800, 320)
        ]

        self.castle_left = DummyCastle(50, 250)
        self.castle_right = DummyCastle(850, 250)

        self.time = 0
        self.score = [0, 0]
        self.game_over = False
        self.winner = None

    def update(self):
        self.time += 1

        # Movimiento enemigos
        for enemy in self.enemies:
            enemy.x -= 1

        # Daño al castillo
        if self.time % 120 == 0:
            self.castle_left.health -= 10

        # Condición de fin
        if self.castle_left.health <= 0:
            self.game_over = True
            self.winner = "Player 2"


class DummyNetwork:
    def __init__(self):
        self.timer = 0
        self.connected = False

    def update(self):
        self.timer += 1
        if self.timer > 180:  # 3 segundos
            self.connected = True