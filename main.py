import pygame
import sys
from network.udp_client import UDPClient
from view.screens.StartScreen import StartScreen
from view.screens.GameScreen import GameScreen
from view.screens.WaitingScreen import WaitingScreen
from view.screens.GameOverScreen import GameOverScreen
from model.player import Player
from model.castle import Castle
from model.game_state import GameState

# Configuración Inicial
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Sockets")
clock = pygame.time.Clock()

client = UDPClient()
client.send_connect()

# Estados y Variables
state = "start"
mis_nombres_locales = []
start_screen    = StartScreen(screen)
waiting_screen  = WaitingScreen(screen)
game_over_screen = GameOverScreen(screen)
game_screen  = None
game_state   = None

def procesar_input_local(player, controles):
    keys = pygame.key.get_pressed()
    accion = None
    old_y = player.y
    if keys[controles['up']] and player.y > 300: player.y -= 5
    if keys[controles['down']] and player.y < 550: player.y += 5
    if keys[controles['shoot']]: accion = "disparar"
    return accion, (player.y != old_y)

running = True
while running:
    clock.tick(60)

    # --- LÓGICA DE RED ---
    while True:
        message, addr = client.receive()
        if not message: break
        
        msg_type = message.get("type")
        payload  = message.get("payload")

        if msg_type == "start_game":
            try:
                var_a = str(payload["team_a"].get("castle", "Castle 1")).split(" ")[-1]
                var_b = str(payload["team_b"].get("castle", "Castle 2")).split(" ")[-1]
                
                p1 = Player(payload["team_a"]["names"][0], "A", 120, 350)
                p2 = Player(payload["team_a"]["names"][1], "A", 120, 450)
                p3 = Player(payload["team_b"]["names"][0], "B", 880, 350)
                p4 = Player(payload["team_b"]["names"][1], "B", 880, 450)
                
                castles = {
                    "A": Castle("A", -70, 250, variant=var_a), 
                    "B": Castle("B", 840, 250, variant=var_b)
                }
                enemy_types = {
                    "A": payload["team_a"].get("enemy", "Troll 1"), 
                    "B": payload["team_b"].get("enemy", "Troll 1")
                }
                
                game_state = GameState([p1, p2, p3, p4], castles, enemy_types)
                game_state.local_players = set(mis_nombres_locales)
                
                game_screen = GameScreen(screen, {
                    "players": [p1, p2, p3, p4], 
                    "castle_a": var_a, "castle_b": var_b,
                    "team_a": payload["team_a"], "team_b": payload["team_b"]
                })
                
                state = "game"
                print("🎮 Estado cambiado a GAME")
            except Exception as e:
                print(f"❌ Error al procesar start_game: {e}")

        elif msg_type == "state_update" and game_state:
            game_state.update_from_server(payload)

        # ← NUEVO: servidor notifica fin de juego
        elif msg_type == "game_over" and game_state:
            if payload.get("winner_team"):
                game_state.winner_team = payload["winner_team"]
            game_state.running = False
            state = "gameover"
            print(f"🏆 Juego terminado — ganador: {game_state.winner_team}")

    # --- EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if state == "start":
            if start_screen.handle_event(event):
                mis_nombres_locales = [start_screen.player1_name, start_screen.player2_name]
                client.send_ready({
                    "names": mis_nombres_locales, 
                    "enemy": start_screen.selected_enemy, 
                    "castle": start_screen.selected_castle
                })
                state = "waiting"

    # --- LÓGICA DE JUEGO ---
    if state == "game" and game_state:
        esquemas = [
            {'up': pygame.K_w,  'down': pygame.K_s,    'shoot': pygame.K_SPACE}, 
            {'up': pygame.K_UP, 'down': pygame.K_DOWN,  'shoot': pygame.K_RETURN}
        ]
        payload_envio = []
        cambio = False
        
        for i, nombre in enumerate(mis_nombres_locales):
            p = game_state.players.get(nombre)
            if p:
                acc, mov = procesar_input_local(p, esquemas[i])
                if mov or acc:
                    cambio = True
                    payload_envio.append({"name": p.name, "x": p.x, "y": p.y, "action": acc})
        
        if cambio:
            client.send_update(payload_envio)
        
        game_state.update_client()

        # ← NUEVO: detectar fin de juego localmente
        if not game_state.running:
            state = "gameover"
            print(f"🏆 Juego terminado — ganador: {game_state.winner_team}")

    # --- DIBUJO ---
    screen.fill((0, 0, 0))
    if state == "start":
        start_screen.draw()
    elif state == "waiting":
        waiting_screen.draw()
    elif state == "game" and game_screen:
        game_screen.draw(game_state)
    elif state == "gameover" and game_state:
        game_over_screen.draw(game_state)

    pygame.display.flip()

client.close()
pygame.quit()
sys.exit()