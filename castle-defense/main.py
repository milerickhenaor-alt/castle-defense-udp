import pygame
from view.screens.StartScreen import StartScreen
from view.screens.WaitingScreen import WaitingScreen
from view.screens.GameScreen import GameScreen
from view.screens.GameOverScreen import GameOverScreen

from view.mock_game_state import DummyGameState, DummyNetwork
from utils.selection_mapper import SelectionMapper

pygame.init()

screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Castle Defense UDP")

clock = pygame.time.Clock()

# ========================
# 🎮 ESTADOS
# ========================
state = "start"

# ========================
# 🖥️ SCREENS
# ========================
start_screen = StartScreen()
waiting_screen = WaitingScreen(screen)
game_screen = None
game_over_screen = GameOverScreen()

# ========================
# 🧠 SIMULACIÓN
# ========================
game_state = DummyGameState()
network = DummyNetwork()

running = True

while running:

    # ========================
    # 🎮 EVENTOS
    # ========================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "start":
            finished = start_screen.handle_event(event)
            if finished:
                state = "waiting"

        elif state == "game":
            # Aquí después irá el controller real
            pass

    # ========================
    # 🧠 LÓGICA
    # ========================
    if state == "waiting":
        waiting_screen.update()
        network.update()

        if network.connected:
            # 🔥 AQUÍ USAMOS EL MAPPER (SOLID)
            selections = {
                "players": SelectionMapper.map_players(start_screen.selected_players),
                "enemy": SelectionMapper.map_enemy(start_screen.selected_enemy),
                "castle": SelectionMapper.map_castle(start_screen.selected_castle),
                "names": [
                    start_screen.player1_name,
                    start_screen.player2_name
                ]
            }

            game_screen = GameScreen(screen, selections)
            state = "game"

    elif state == "game":
        game_state.update()

        if game_state.game_over:
            state = "game_over"

    # ========================
    # 🎨 RENDER
    # ========================
    screen.fill((0, 0, 0))

    if state == "start":
        start_screen.draw(screen)

    elif state == "waiting":
        waiting_screen.draw()

    elif state == "game":
        if game_screen:
            game_screen.update(game_state)
            game_screen.draw(screen)

    elif state == "game_over":
        game_over_screen.draw(screen, game_state)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()