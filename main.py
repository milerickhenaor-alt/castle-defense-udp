import pygame
from model import *
from view import *

client = UDPClient()
client.send_connect()

running = True
while running:
    clock.tick(60)

    # ================= 1. RED (RECEPCIÓN CONSTANTE) =================
    while True:
        message, addr = client.receive()
        if not message:
            break
        
        msg_type = message.get("type")
        payload = message.get("payload")

        if msg_type == "start_game":
            print("Mensaje start_game recibido. Inicializando...")
            # Extraer variantes de castillo (ej: "Variant 1" -> "1")
            var_a = str(payload["team_a"]["castle"]).split(" ")[-1]
            var_b = str(payload["team_b"]["castle"]).split(" ")[-1]

            p1 = Player(payload["team_a"]["names"][0], "A", 120, 350)
            p2 = Player(payload["team_a"]["names"][1], "A", 120, 450)
            p3 = Player(payload["team_b"]["names"][0], "B", 880, 350)
            p4 = Player(payload["team_b"]["names"][1], "B", 880, 450)

            castles = {
                "A": Castle("A", -70, 250, variant=var_a),
                "B": Castle("B", 840, 250, variant=var_b)
            }

            enemy_types = {"A": payload["team_a"]["enemy"], "B": payload["team_b"]["enemy"]}
            
            game_state = GameState([p1, p2, p3, p4], castles, enemy_types)
            game_state.local_players = set(mis_nombres_locales)

            selections = {
                "players": [p1, p2, p3, p4],
                "castle_a": var_a, "castle_b": var_b,
                "team_a": payload["team_a"], "team_b": payload["team_b"]
            }

            game_screen = GameScreen(screen, selections)
            state = "game"  # CAMBIO DE ESTADO

        elif msg_type == "state_update" and game_state:
            game_state.update_from_server(payload)

    # ================= 2. EVENTOS DE ENTRADA =================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "start":
            if start_screen.handle_event(event):
                mis_nombres_locales = [start_screen.player1_name, start_screen.player2_name]
                datos = {
                    "names": mis_nombres_locales,
                    "enemy": start_screen.selected_enemy,
                    "castle": start_screen.selected_castle
                }
                client.send_ready(datos)
                state = "waiting"

    # ================= 3. LÓGICA DE JUEGO =================
    if state == "game" and game_state:
        # (Tu lógica de esquemas de control y client.send_update se mantiene igual)
        # ... 
        game_state.update_client()

    # ================= 4. RENDERIZADO =================
    screen.fill((0, 0, 0))
    if state == "start": start_screen.draw()
    elif state == "waiting": waiting_screen.draw()
    elif state == "game" and game_screen: game_screen.draw(game_state)
    
    pygame.display.flip()

client.close()
pygame.quit()