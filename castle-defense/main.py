import pygame
import sys
from network.udp_client import UDPClient
from view.screens.StartScreen import StartScreen
from view.screens.GameScreen import GameScreen
from view.screens.WaitingScreen import WaitingScreen
from model.player import Player
from model.castle import Castle
from model.game_state import GameState

# ================= CONFIG =================
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Castle Defense 2vs2 - UDP PRO")
clock = pygame.time.Clock()

client = UDPClient()
client.send_connect()

# ================= ESTADOS =================
state = "start"
mis_nombres_locales = []

start_screen = StartScreen(screen)
waiting_screen = WaitingScreen(screen)
game_screen = None
game_state = None

# ================= INPUT LOCAL =================
def procesar_input_local(player, controles):
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

# ================= LOOP =================
running = True
while running:
    clock.tick(60)

    # ================= RED (RECIBIR TODO EL BUFFER) =================
    while True:
        message, addr = client.receive()
        if not message:
            break

        msg_type = message.get("type")
        payload = message.get("payload")

        # ===== INICIO DE PARTIDA =====
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

            enemy_types = {
                "A": payload["team_a"]["enemy"],
                "B": payload["team_b"]["enemy"]
            }

            game_state = GameState(all_players, castles, enemy_types)
            game_state.local_players = set(mis_nombres_locales)

            selections = {
                "players": all_players,
                "castle_a": var_a,
                "castle_b": var_b,
                "team_a": payload["team_a"],
                "team_b": payload["team_b"]
            }

            game_screen = GameScreen(screen, selections)
            state = "game"

        # ===== SINCRONIZACIÓN REAL =====
        elif msg_type == "state_update" and game_state:
            game_state.update_from_server(payload)

    # ================= EVENTOS =================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "start":
            if start_screen.handle_event(event):
                mis_nombres_locales = [
                    start_screen.player1_name,
                    start_screen.player2_name
                ]

                datos = {
                    "names": mis_nombres_locales,
                    "enemy": start_screen.selected_enemy,
                    "castle": start_screen.selected_castle
                }

                client.send_ready(datos)
                state = "waiting"

    # ================= LÓGICA LOCAL =================
    if state == "game" and game_state:

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

        # 🔥 SOLO ENVÍA SI HAY CAMBIOS (CLAVE PARA EL LAG)
        if hubo_cambio:
            client.send_update(payload_local)

        game_state.update_client()

    # ================= RENDER =================
    screen.fill((0, 0, 0))

    if state == "start":
        start_screen.draw()

    elif state == "waiting":
        waiting_screen.draw()

    elif state == "game" and game_screen:
        game_screen.draw(game_state)

    pygame.display.flip()

# ================= SALIDA =================
client.close()
pygame.quit()
sys.exit()