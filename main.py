"""Punto de entrada del juego Castle Defense.

Maneja:
  - Inicialización de Pygame y cliente UDP
  - Flujo de pantallas (inicio, espera, juego, fin)
  - Sincronización de red (envío de datos de jugador, recepción de estado)
  - Renderizado y entrada de usuario
"""

import pygame
import sys
import os
from network.udp_client import UDPClient
from view.screens.StartScreen import StartScreen
from view.screens.GameScreen import GameScreen
from view.screens.WaitingScreen import WaitingScreen
from view.screens.GameOverScreen import GameOverScreen
from model.player import Player
from model.castle import Castle
from model.game_state import GameState
from controller.input_handler import process_input_local

# --- CONFIGURACIÓN PYGAME Y RED ---
"""Inicializa ventana, pantalla y cliente UDP."""
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Sockets")
clock = pygame.time.Clock()

client = UDPClient()
client.send_connect()

# --- MÁQUINA DE ESTADOS DEL JUEGO ---
"""Estados posibles: 'start' (menú), 'waiting' (esperando rival),
'game' (partida en curso), 'game_over' (fin de partida)."""
state = "start"
mis_nombres_locales = []
start_screen = StartScreen(screen)
waiting_screen = WaitingScreen(screen)
game_over_screen = GameOverScreen(screen)
game_screen = None
game_state = None

running = True

# --- BUCLE PRINCIPAL DEL JUEGO ---
"""Ciclo a 60 FPS que maneja: red, eventos, lógica y renderizado."""
while running:
    clock.tick(60)

    # FASE 1: RECIBIR MENSAJES DEL SERVIDOR
    """Procesa actualizaciones de estado del juego y cambios de pantalla."""
    while True:
        message, addr = client.receive()
        if not message: break
        
        msg_type = message.get("type")
        payload = message.get("payload")

        if msg_type == "start_game":
            try:
                var_a = str(payload["team_a"].get("castle", "1")).split(" ")[-1]
                var_b = str(payload["team_b"].get("castle", "2")).split(" ")[-1]
                
                players = [
                    Player(payload["team_a"]["names"][0], "A", 160, 350),
                    Player(payload["team_a"]["names"][1], "A", 160, 450),
                    Player(payload["team_b"]["names"][0], "B", 845, 350),
                    Player(payload["team_b"]["names"][1], "B", 845, 450)
                ]
                
                castles = {
                    "A": Castle("A", -70, 250, variant=var_a), 
                    "B": Castle("B", 840, 250, variant=var_b)
                }
                
                enemy_types = {
                    "A": payload["team_a"].get("enemy", "Troll 1"), 
                    "B": payload["team_b"].get("enemy", "Troll 1")
                }
                
                game_state = GameState(players, castles, enemy_types)
                game_screen = GameScreen(screen, {
                    "players": players, 
                    "castle_a": var_a, "castle_b": var_b,
                    "enemy_types": enemy_types
                })
                state = "game"
            except Exception as e:
                print(f"❌ Error al iniciar: {e}")

        elif msg_type == "state_update" and game_state:
            game_state.update_from_dict(payload)
            if not payload.get("running", True):
                state = "game_over"

    # FASE 2: PROCESAR ENTRADA DEL JUGADOR
    # Captura teclado para movimiento y disparo
    events = pygame.event.get()

    # 🔥 NUEVO: detectar disparos por KEYDOWN
    disparos = set()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                disparos.add(0)  # jugador 1
            if event.key == pygame.K_SPACE:
                disparos.add(1)  # jugador 2

        if state == "start":
            if start_screen.handle_event(event):
                mis_nombres_locales = [start_screen.player1_name, start_screen.player2_name]
                client.send_ready({
                    "names": mis_nombres_locales, 
                    "enemy": start_screen.selected_enemy, 
                    "castle": start_screen.selected_castle
                })
                state = "waiting"

    # FASE 3: ACTUALIZAR LÓGICA DEL JUEGO
    """Sincroniza movimientos de jugadores locales y recibe estado del servidor."""
    if state == "game" and game_state:
        esquemas = [
            {'up': pygame.K_w, 'down': pygame.K_s, 'shoot': pygame.K_f},
            {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'shoot': pygame.K_SPACE}
        ]

        datos_a_enviar = []
        hubo_cambio = False

        for i, nombre in enumerate(mis_nombres_locales):
            p = game_state.players.get(nombre)
            if p:
                accion, movido = process_input_local(p, esquemas[i])

                disparo = i in disparos  # 🔥 NUEVO

                if movido or disparo:
                    payload = {
                        "name": p.name,
                        "x": p.x,
                        "y": p.y,
                        "action": "shoot" if disparo else None
                    }
                    datos_a_enviar.append(payload)
                    hubo_cambio = True

        if hubo_cambio:
            client.send_update(datos_a_enviar)

        game_state.update_client()

    # FASE 4: RENDERIZAR PANTALLA
    """Dibuja según el estado actual del juego."""
    screen.fill((0, 0, 0)) 
    if state == "start": start_screen.draw()
    elif state == "waiting": waiting_screen.draw()
    elif state == "game": game_screen.draw(game_state)
    elif state == "game_over": game_over_screen.draw(game_state) 
    if game_over_screen.handle_event(event):
            state = "start"
            game_state = None

    # FASE 3: ACTUALIZAR LÓGICA
    
    pygame.display.flip()

# --- LIMPIEZA ---
"""Cierra conexión y libera recursos."""
client.close()
pygame.quit()