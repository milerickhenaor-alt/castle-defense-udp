import pygame

def procesar_input(jugadores):
    acciones = []

    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Solo click izquierdo
    if click[0]:
        for jugador in jugadores:
            acciones.append({
                "jugador_id": jugador.id,
                "accion": "disparar",
                "posicion": mouse_pos
            })

    return acciones