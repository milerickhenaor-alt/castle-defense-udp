import pygame
import sys
from network.udp_client import UDPClient
from view.screens.StartScreen import StartScreen
from view.screens.GameScreen import GameScreen
from view.screens.WaitingScreen import WaitingScreen
from model.player import Player
from model.castle import Castle
from model.game_state import GameState

pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

client = UDPClient()
client.send_connect()

state = "start"
mi_nombre = "" # Se llenará al elegir en StartScreen
start_screen = StartScreen(screen)
waiting_screen = WaitingScreen(screen)
game_screen = None
game_state = None

running = True
while running:
    clock.tick(60)
    
    # --- 1. RED: Recibir datos ---
    message, addr = client.receive()
    if message:
        msg_type = message.get("type")
        payload = message.get("payload")

        if msg_type == "start_game":
            # Extraer variantes y tipos de Trolls
            var_a = str(payload["team_a"]["castle"]).split(" ")[-1]
            var_b = str(payload["team_b"]["castle"]).split(" ")[-1]
            enemy_a = payload["team_a"]["enemy"]
            enemy_b = payload["team_b"]["enemy"]

            # Crear Jugadores
            p1 = Player(payload["team_a"]["names"][0], "A", 120, 350)
            p2 = Player(payload["team_a"]["names"][1], "A", 120, 450)
            p3 = Player(payload["team_b"]["names"][0], "B", 880, 350)
            p4 = Player(payload["team_b"]["names"][1], "B", 880, 450)
            
            all_players = [p1, p2, p3, p4]
            castles = {
                "A": Castle("A", 10, 250, variant=var_a),
                "B": Castle("B", 760, 250, variant=var_b)
            }
            
            # Inicializar Lógica con tipos de Trolls
            enemy_types = {"A": enemy_a, "B": enemy_b}
            game_state = GameState(all_players, castles, enemy_types)
            
            # Inicializar Renderer
            selections = {
                "players": all_players,
                "castle_a": var_a, "castle_b": var_b,
                "team_a": payload["team_a"], "team_b": payload["team_b"]
            }
            game_screen = GameScreen(screen, selections)
            state = "game"

        elif msg_type == "game_update" and game_state:
            # Sincronizar posiciones de los otros
            game_state.update_from_server(payload)

    # --- 2. EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if state == "start":
            if start_screen.handle_event(event):
                mi_nombre = start_screen.player1_name # Guardamos quién soy yo
                mis_datos = {
                    "names": [start_screen.player1_name, start_screen.player2_name],
                    "enemy": start_screen.selected_enemy,
                    "castle": start_screen.selected_castle
                }
                client.send_ready(mis_datos)
                state = "waiting"

   
    # --- 3. ACTUALIZACIÓN ---
    if state == "game" and game_state:
        # Buscamos a nuestro personaje por el nombre que guardamos en la StartScreen
        yo = game_state.players.get(mi_nombre)
        
        if yo:
            keys = pygame.key.get_pressed()
            old_y = yo.y
            
            # Movimiento con límites de pantalla para que no te salgas
            if keys[pygame.K_w] and yo.y > 300: 
                yo.y -= 5
            if keys[pygame.K_s] and yo.y < 550: 
                yo.y += 5
            
            # 🔥 OPTIMIZACIÓN: Solo enviamos al servidor SI nos movimos.
            # Esto reduce el lag drásticamente.
            if yo.y != old_y:
                client.send_update({
                    "name": mi_nombre, 
                    "x": yo.x, 
                    "y": yo.y
                })
        
        # La lógica local (Trolls moviéndose, colisiones, etc.)
        game_state.update()

    # --- 4. DIBUJO ---
    screen.fill((0, 0, 0))
    if state == "start": start_screen.draw()
    elif state == "waiting": waiting_screen.draw()
    elif state == "game" and game_screen: game_screen.draw(game_state)

    pygame.display.flip()

client.close()
pygame.quit()