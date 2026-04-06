import pygame

# Screens
from view.screens.StartScreen import StartScreen
from view.screens.GameScreen import GameScreen
from view.screens.WaitingScreen import WaitingScreen

# Model
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
state = "start"

start_screen = StartScreen(screen)
waiting_screen = WaitingScreen(screen)
game_screen = None

game_state = None

running = True

# ─────────────────────────────
# LOOP PRINCIPAL
# ─────────────────────────────
while running:
    clock.tick(60)

    # EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "start":
            finished = start_screen.handle_event(event)
            if finished:
                state = "waiting"

        elif state == "waiting":
            waiting_screen.handle_event(event)

        elif state == "game":
            pass

    # LÓGICA
    if state == "waiting":
        waiting_screen.update()

        if waiting_screen.is_ready:
            selections = {
                "players": start_screen.selected_players,
                "enemy": start_screen.selected_enemy,
                "castle": start_screen.selected_castle,
                "names": [
                    start_screen.player1_name,
                    start_screen.player2_name
                ]
            }

            players = [
                Player(selections["names"][0], "A", 150, 300),
                Player(selections["names"][1], "B", 850, 300)
            ]
         
            castles = {
                "A": Castle("A", -70, 250),
                "B": Castle("B", 840, 250)
            }

            game_state = GameState(players, castles)

            game_screen = GameScreen(screen, selections)

            state = "game"

    elif state == "game":
        game_state.update()
        game_screen.update(game_state)

    # DIBUJO
    screen.fill((0, 0, 0))

    if state == "start":
        start_screen.draw()

    elif state == "waiting":
        waiting_screen.draw()

    elif state == "game":
        game_screen.draw(game_state)

    pygame.display.flip()

pygame.quit()