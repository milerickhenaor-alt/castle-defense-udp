import pygame

def process_input_local(player, controles):
    """
    player: El objeto Player del modelo.
    controles: Diccionario con {up, down, shoot}.
    """
    keys = pygame.key.get_pressed()
    accion = None
    old_y = player.y

    # Movimiento Vertical
    if keys[controles['up']] and player.y > 300:
        player.y -= 5
    if keys[controles['down']] and player.y < 550:
        player.y += 5

    # Acción de Disparo
    if keys[controles['shoot']]:
        accion = "disparar"
        
    se_movio = (player.y != old_y)
    return accion, se_movio
