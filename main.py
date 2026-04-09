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
import pygame
import sys
from network.udp_client import UDPClient
from view.screens.StartScreen import StartScreen
from view.screens.GameScreen import GameScreen
from view.screens.WaitingScreen import WaitingScreen
from model.player import Player
from model.castle import Castle
from model.game_state import GameState

# --- CONFIGURACIÓN INICIAL ---
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Castle Defense 2vs2 - Sockets UDP")
clock = pygame.time.Clock()

client = UDPClient()
client.send_connect()

# Estados de flujo
state = "start"
mis_nombres_locales = [] 
start_screen = StartScreen(screen)
waiting_screen = WaitingScreen(screen)
game_screen = None
game_state = None

def procesar_input_local(player, controles):
    """
    Maneja el movimiento y disparo de un jugador específico.
    Retorna (accion, se_movio)
    """
    keys = pygame.key.get_pressed()
    accion = None
    old_y = player.y

    # Movimiento vertical con límites de carril
    if keys[controles['up']] and player.y > 300:
        player.y -= 5
    if keys[controles['down']] and player.y < 550:
        player.y += 5

    # Acción de disparo
    if keys[controles['shoot']]:
        accion = "disparar"
        
    se_movio = (player.y != old_y)
    return accion, se_movio

running = True
while running:
    clock.tick(60) 
    
    # --- 1. RED: RECIBIR DATOS DEL SERVIDOR ---
    message, addr = client.receive()
    if message:
        msg_type = message.get("type")
        payload = message.get("payload")

        if msg_type == "start_game":
            var_a = str(payload["team_a"]["castle"]).split(" ")[-1]
            var_b = str(payload["team_b"]["castle"]).split(" ")[-1]
            
            p1 = Player(payload["team_a"]["names"][0], "A", 120, 350)
            p2 = Player(payload["team_a"]["names"][1], "A", 120, 450)
            p3 = Player(payload["team_b"]["names"][0], "B", 880, 350)
            p4 = Player(payload["team_b"]["names"][1], "B", 880, 450)
            
            all_players = [p1, p2, p3, p4]
            castles = {
                "A": Castle("A", -70, 250, variant=var_a),
                "B": Castle("B", 840, 250, variant=var_b)
            }
            
            enemy_types = {"A": payload["team_a"]["enemy"], "B": payload["team_b"]["enemy"]}
            game_state = GameState(all_players, castles, enemy_types)
            game_state.local_players = set(mis_nombres_locales)
            
            selections = {
                "players": all_players,
                "castle_a": var_a, "castle_b": var_b,
                "team_a": payload["team_a"], "team_b": payload["team_b"]
            }
            game_screen = GameScreen(screen, selections)
            state = "game"

        elif msg_type == "state_update" and game_state:
            # Sincronización maestra (Trolls, proyectiles y otros jugadores)
            game_state.update_from_server(payload)

    # --- 2. EVENTOS GLOBALES ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if state == "start":
            if start_screen.handle_event(event):
                mis_nombres_locales = [start_screen.player1_name, start_screen.player2_name]
                mis_datos = {
                    "names": mis_nombres_locales,
                    "enemy": start_screen.selected_enemy,
                    "castle": start_screen.selected_castle
                }
                client.send_ready(mis_datos)
                state = "waiting"

    # --- 3. ACTUALIZACIÓN DE LÓGICA Y INPUT LOCAL ---
    if state == "game" and game_state:
        # Definición de controles: Jugador 1 (W/S/Espacio) y Jugador 2 (Flechas/Enter)
        esquemas = [
            {'up': pygame.K_w, 'down': pygame.K_s, 'shoot': pygame.K_SPACE},
            {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'shoot': pygame.K_RETURN}
        ]

        hubo_actividad = False
        payload_local = []

        # Procesar a los dos jugadores que controla esta PC
        for i, nombre in enumerate(mis_nombres_locales):
            p_obj = game_state.players.get(nombre)
            if p_obj:
                accion, se_movio = procesar_input_local(p_obj, esquemas[i])
                
                if se_movio or accion == "disparar":
                    hubo_actividad = True
                
                payload_local.append({
                    "name": p_obj.name,
                    "x": p_obj.x,
                    "y": p_obj.y,
                    "action": accion
                })

        # Enviar actualización al servidor si hubo cambios
        client.send_update(payload_local)
        game_state.update_client()

    # --- 4. RENDERIZADO ---
    screen.fill((0, 0, 0))

    if state == "start":
        start_screen.draw()
    elif state == "waiting":
        waiting_screen.draw()
    elif state == "game" and game_screen:
        game_screen.draw(game_state)

    pygame.display.flip()

client.close()
pygame.quit()
sys.exit()
    # Acción de Disparo
    if keys[controles['shoot']]:
        accion = "disparar"
        
    se_movio = (player.y != old_y)
    return accion, se_movio
