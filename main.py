import pygame
import sys

# Importaciones de Red
from network.udp_client import UDPClient

# Importaciones de Vistas (Pantallas)
from view.screens.StartScreen import StartScreen
from view.screens.GameScreen import GameScreen
from view.screens.WaitingScreen import WaitingScreen

# Importaciones de Modelos
from model.player import Player
from model.castle import Castle
from model.game_state import GameState

# ================= CONFIGURACIÓN INICIAL =================
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Castle Defense 2vs2 - UDP Multijugador")
clock = pygame.time.Clock()

# Inicializar Cliente UDP y conectar
client = UDPClient()
client.send_connect()

# ================= ESTADOS Y VARIABLES GLOBALES =================
state = "start"
mis_nombres_locales = []

# Inicializar pantallas
start_screen = StartScreen(screen)
waiting_screen = WaitingScreen(screen)
game_screen = None
game_state = None

# ================= FUNCIÓN DE CONTROL LOCAL =================
def procesar_input_local(player, controles):
    """Maneja el movimiento y disparo de los jugadores controlados en esta PC."""
    keys = pygame.key.get_pressed()
    accion = None
    old_y = player.y

    if keys[controles['up']] and player.y > 300:
        player.y -= 5
    if keys[controles['down']] and player.y < 550:
        player.y += 5

    if keys[controles['shoot']]:
        accion = "disparar"

    se_movio = (player.y != old_y)
    return accion, se_movio

# ================= LOOP PRINCIPAL =================
running = True
while running:
    clock.tick(60)

    # ================= 1. PROCESAMIENTO DE RED (SIEMPRE ACTIVO) =================
    # Vaciamos el buffer de red en cada frame para evitar lag acumulado
    while True:
        message, addr = client.receive()
        if not message:
            break

        msg_type = message.get("type")
        payload = message.get("payload")

        # EVENTO: El servidor inicia la partida
        if msg_type == "start_game":
            print("¡Partida iniciada por el servidor!")
            
            # Extraer variantes de castillos
            var_a = str(payload["team_a"]["castle"]).split(" ")[-1]
            var_b = str(payload["team_b"]["castle"]).split(" ")[-1]

            # Crear instancias de jugadores (2 por equipo)
            p1 = Player(payload["team_a"]["names"][0], "A", 120, 350)
            p2 = Player(payload["team_a"]["names"][1], "A", 120, 450)
            p3 = Player(payload["team_b"]["names"][0], "B", 880, 350)
            p4 = Player(payload["team_b"]["names"][1], "B", 880, 450)

            all_players = [p1, p2, p3, p4]

            castles = {
                "A": Castle("A", -70, 250, variant=var_a),
                "B": Castle("B", 840, 250, variant=var_b)
            }

            enemy_types = {
                "A": payload["team_a"]["enemy"],
                "B": payload["team_b"]["enemy"]
            }

            # Inicializar el estado lógico del juego
            game_state = GameState(all_players, castles, enemy_types)
            game_state.local_players = set(mis_nombres_locales)

            # Preparar la pantalla de juego
            selections = {
                "players": all_players,
                "castle_a": var_a,
                "castle_b": var_b,
                "team_a": payload["team_a"],
                "team_b": payload["team_b"]
            }

            game_screen = GameScreen(screen, selections)
            state = "game" # Transición a la pantalla de juego

        # EVENTO: Actualización de posiciones/acciones de otros jugadores
        elif msg_type == "state_update" and game_state:
            game_state.update_from_server(payload)

    # ================= 2. MANEJO DE EVENTOS PYGAME =================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Eventos exclusivos de la pantalla inicial
        if state == "start":
            if start_screen.handle_event(event):
                mis_nombres_locales = [
                    start_screen.player1_name,
                    start_screen.player2_name
                ]

                datos_ready = {
                    "names": mis_nombres_locales,
                    "enemy": start_screen.selected_enemy,
                    "castle": start_screen.selected_castle
                }

                client.send_ready(datos_ready)
                state = "waiting" # Esperar a que el servidor diga "start_game"

    # ================= 3. LÓGICA DE JUEGO (DURANTE LA PARTIDA) =================
    if state == "game" and game_state:
        # Configuración de teclas para los dos jugadores locales
        esquemas = [
            {'up': pygame.K_w, 'down': pygame.K_s, 'shoot': pygame.K_SPACE},
            {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'shoot': pygame.K_RETURN}
        ]

        payload_local = []
        hubo_cambio = False

        for i, nombre in enumerate(mis_nombres_locales):
            player = game_state.players.get(nombre)

            if player:
                accion, se_movio = procesar_input_local(player, esquemas[i])

                if se_movio or accion:
                    hubo_cambio = True
                    payload_local.append({
                        "name": player.name,
                        "x": player.x,
                        "y": player.y,
                        "action": accion
                    })

        # Enviamos actualización al servidor solo si el jugador hizo algo
        if hubo_cambio:
            client.send_update(payload_local)

        # Actualización de física local (balas, colisiones, etc.)
        game_state.update_client()

    # ================= 4. RENDERIZADO =================
    screen.fill((0, 0, 0))

    if state == "start":
        start_screen.draw()

    elif state == "waiting":
        waiting_screen.draw()

    elif state == "game" and game_screen:
        game_screen.draw(game_state)

    pygame.display.flip()

# ================= FINALIZACIÓN =================
client.close()
pygame.quit()
sys.exit()