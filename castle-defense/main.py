import pygame
import sys

# Networking
from network.udp_client import UDPClient

# Screens
from view.screens.StartScreen import StartScreen
from view.screens.GameScreen import GameScreen
from view.screens.WaitingScreen import WaitingScreen

# Model
from model.player import Player
from model.castle import Castle
from model.game_state import GameState

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN INICIAL
# ─────────────────────────────────────────────────────────────────────────────
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Castle Defense 2vs2 - Online")

clock = pygame.time.Clock()

# El cliente se crea una sola vez para mantener la misma conexión
client = UDPClient()
client.send_connect()

# Estados: "start" -> "waiting" -> "game"
state = "start"

start_screen = StartScreen(screen)
waiting_screen = WaitingScreen(screen)
game_screen = None
game_state = None

running = True

# ─────────────────────────────────────────────────────────────────────────────
# LOOP PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
while running:
    clock.tick(60)
    
    # --- 1. RED: ESCUCHAR SIEMPRE ---
    # Esto es lo que permite que el servidor nos saque de "waiting"
    message, addr = client.receive()
    if message:
        msg_type = message.get("type")
        payload = message.get("payload")

        if msg_type == "start_game":
            payload = message["payload"]
            
            # 1. Limpieza de variantes
            var_a = str(payload["team_a"]["castle"]).split(" ")[-1]
            var_b = str(payload["team_b"]["castle"]).split(" ")[-1]

            # 2. Creación de Objetos (Jugadores y Castillos)
            p1 = Player(payload["team_a"]["names"][0], "A", 120, 350)
            p2 = Player(payload["team_a"]["names"][1], "A", 120, 450)
            p3 = Player(payload["team_b"]["names"][0], "B", 880, 350)
            p4 = Player(payload["team_b"]["names"][1], "B", 880, 450)
            
            all_players = [p1, p2, p3, p4]
            
            castles = {
                "A": Castle("A", 10, 250, variant=var_a),
                "B": Castle("B", 760, 250, variant=var_b)
            }
            
            # 3. Formatear las selecciones para el Renderer
            # Aquí es donde arreglamos el KeyError: 'players'
            selections_for_renderer = {
                "players": all_players,  # La lista de los 4 objetos Player creados
                "castle_a": var_a,       # El número de variante del equipo A
                "castle_b": var_b,
                "team_a": payload["team_a"],
                "team_b": payload["team_b"]
            }

            # 4. Inicializar estados
            game_state = GameState(all_players, castles, map_width=WIDTH, map_height=HEIGHT)
            
            # Pasamos el diccionario corregido
            game_screen = GameScreen(screen, selections_for_renderer)
            
            state = "game"

    # --- 2. EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "start":
            # Si el usuario termina de elegir en la pantalla de inicio
            if start_screen.handle_event(event):
                mis_datos = {
                    "names": [start_screen.player1_name, start_screen.player2_name],
                    "enemy": start_screen.selected_enemy,
                    "castle": start_screen.selected_castle
                }
                # Informamos al server que este equipo está listo
                client.send_ready(mis_datos)
                state = "waiting"

        elif state == "game":
            # Manejo de inputs del juego (disparos, etc)
            pass

    # --- 3. ACTUALIZACIÓN ---
    if state == "game" and game_state:
        game_state.update()

    # --- 4. DIBUJO ---
    screen.fill((0, 0, 0))

    if state == "start":
        start_screen.draw()
    elif state == "waiting":
        waiting_screen.draw()
    elif state == "game" and game_screen:
        game_screen.draw(game_state)

    pygame.display.flip()

# Cierre limpio
client.close()
pygame.quit()
sys.exit()