import pygame
from controller.input_handler import procesar_input

def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    game_state = None
    renderer = None
    network = None

    #Son 4 jugadores
    jugadores = []

    running = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # INPUT
        acciones = procesar_input(jugadores)

        # ACCIONES
        for accion in acciones:
            if accion["accion"] == "disparar":
                print(f"Jugador {accion['jugador_id']} disparó en {accion['posicion']}")

        # UPDATE
        if game_state:
            game_state.update()

        # NETWORK
        if network:
            for accion in acciones:
                network.send(accion)
            data = network.receive()

        # RENDER
        if renderer:
            renderer.draw(screen, game_state)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
