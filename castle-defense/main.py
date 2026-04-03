import pygame
from view.screens.StartScreen import StartScreen
from view.screens.GameScreen import GameScreen
from view.screens.GameOverScreen import GameOverScreen

pygame.init()
screen = pygame.display.set_mode((1000, 600))

state = "start"

start_screen = StartScreen()
game_screen = None
game_over_screen = GameOverScreen()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "start":
            finished = start_screen.handle_event(event)
            if finished:
                selections = {
                    "players": start_screen.selected_players,
                    "enemy": start_screen.selected_enemy,
                    "castle": start_screen.selected_castle
                }
                game_screen = GameScreen(screen, selections)
                state = "game"

    if state == "start":
        start_screen.draw(screen)

    elif state == "game":
        # aquí irá game_state real
        class Dummy: pass
        game_state = Dummy()
        game_state.players = []
        game_state.enemies = []
        game_state.castle_left = Dummy()
        game_state.castle_right = Dummy()
        game_state.score_left = 10
        game_state.score_right = 5
        game_state.time_left = 50

        game_screen.update(game_state)

        if game_state.time_left <= 0:
            state = "game_over"

    elif state == "game_over":
        game_over_screen.draw(screen, game_state)

pygame.quit()