import pygame
from view.screens.StartScreen import StartScreen
from view.screens.GameScreen import GameScreen # Asegúrate de que existan
from view.screens.GameOverScreen import GameOverScreen

pygame.init()
screen = pygame.display.set_mode((1000, 600))
clock = pygame.time.Clock() # <--- 1. Agrega un reloj

state = "start"
start_screen = StartScreen()
game_screen = None
game_over_screen = GameOverScreen() 

running = True

while running:
    # --- PROCESAMIENTO DE EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "start":
            finished = start_screen.handle_event(event)
            if finished:
                selections = {
                    "players": start_screen.selected_players,
                    "enemy": start_screen.selected_enemy,
                    "castle": start_screen.selected_castle,
                    "names": [start_screen.player1_name, start_screen.player2_name]
                }
                game_screen = GameScreen(screen, selections)
                state = "game"

    # --- LÓGICA Y DIBUJO ---
    # Limpiar pantalla siempre al inicio del frame
    screen.fill((0, 0, 0)) 

    if state == "start":
        start_screen.draw(screen)

    elif state == "game":
        # Simulación de estado de juego (Dummy)
        class Dummy: pass
        game_state = Dummy()
        game_state.time_left = 50 
        
        game_screen.draw(screen) # <--- Asegúrate de llamar al draw de game_screen
        game_screen.update(game_state)

        if game_state.time_left <= 0:
            state = "game_over"

    elif state == "game_over":
        pass # game_over_screen.draw(screen, game_state)

    # --- LO MÁS IMPORTANTE ---
    pygame.display.flip() # <--- 2. Actualiza la pantalla completa
    clock.tick(60)        # <--- 3. Limita a 60 FPS (evita pantalla negra por lag)

pygame.quit()