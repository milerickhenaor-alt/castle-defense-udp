import pygame

# Screens
from view.screens.StartScreen import StartScreen
from view.screens.GameScreen import GameScreen
from view.screens.WaitingScreen import WaitingScreen

# Model real
from model.player import Player
from model.castle import Castle
from model.game_state import GameState


pygame.init()
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Castle Defense")

clock = pygame.time.Clock()

# ─────────────────────────────
# ESTADOS
# ─────────────────────────────
STATE_START = "start"
STATE_WAITING = "waiting"
STATE_GAME = "game"

state = STATE_START

# ─────────────────────────────
# SCREENS
# ─────────────────────────────
start_screen = StartScreen(screen)
waiting_screen = WaitingScreen(screen)
game_screen = None

# ─────────────────────────────
# MODEL
# ─────────────────────────────
game_state = None

running = True

while running:
    clock.tick(60)

    # ─────────────────────────────
    # EVENTOS
    # ─────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == STATE_START:
            finished = start_screen.handle_event(event)
            if finished:
                state = STATE_WAITING

        elif state == STATE_WAITING:
            waiting_screen.handle_event(event)

        elif state == STATE_GAME:
            pass  # aquí irá el controller luego

    # ─────────────────────────────
    # LÓGICA
    # ─────────────────────────────
    if state == STATE_WAITING:
        waiting_screen.update()

        if waiting_screen.is_ready:

            # 🔥 TRANSFORMAR SELECTIONS (MUY IMPORTANTE)
            def parse_player(player_str):
                # "Fairy 1" → {"type": "Fairies", "variant": "1"}
                parts = player_str.split()
                return {
                    "type": parts[0] + "s",   # Fairy → Fairies
                    "variant": parts[1]
                }

            selections = {
                "players": [
                    parse_player(start_screen.selected_players[0]),
                    parse_player(start_screen.selected_players[1])
                ],
                "enemy": start_screen.selected_enemy.split()[1],   # "Troll 1" → "1"
                "castle": start_screen.selected_castle.split()[1], # "Castle 1" → "1"
                "names": [
                    start_screen.player1_name,
                    start_screen.player2_name
                ]
            }

            # ─────────────────────────────
            # CREAR MODEL REAL
            # ─────────────────────────────
            players = [
                Player(
                    name=selections["names"][0],
                    team="A",
                    x=150,
                    y=300
                ),
                Player(
                    name=selections["names"][1],
                    team="B",
                    x=750,
                    y=300
                )
            ]

            castles = {
                "A": Castle(team="A", x=50, y=250),
                "B": Castle(team="B", x=900, y=250)
            }

            game_state = GameState(players, castles)

            game_screen = GameScreen(screen, selections)

            state = STATE_GAME

    elif state == STATE_GAME:
        game_state.update()
        game_screen.update(game_state)

    # ─────────────────────────────
    # DIBUJO
    # ─────────────────────────────
    screen.fill((0, 0, 0))

    if state == STATE_START:
        start_screen.draw()

    elif state == STATE_WAITING:
        waiting_screen.draw(screen)  # 🔥 FIX

    elif state == STATE_GAME:
        # ⚠️ IMPORTANTE: GameScreen ya dibuja internamente
        game_screen.update(game_state)

    pygame.display.flip()

pygame.quit()