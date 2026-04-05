import pygame

def procesar_input(player):
    keys = pygame.key.get_pressed()
    accion = None

    if keys[pygame.K_w]:
        player.y -= 5
    if keys[pygame.K_s]:
        player.y += 5
    if keys[pygame.K_a]:
        player.x -= 5
    if keys[pygame.K_d]:
        player.x += 5

    if keys[pygame.K_SPACE]:
        accion = "disparar"

    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if click[0]:  # click izquierdo
        accion = "disparar"
        
    return accion