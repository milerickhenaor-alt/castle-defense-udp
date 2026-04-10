import pygame
import sys
import os
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
pygame.display.set_caption("Tower Defense Sockets - Multijugador")
clock = pygame.time.Clock()

client = UDPClient()
client.send_connect()

# --- ESTADOS Y VARIABLES ---
state = "start"
mis_nombres_locales = []
start_screen = StartScreen(screen)
waiting_screen = WaitingScreen(screen)
game_screen = None
game_state = None

def procesar_input_local(player, controles):
    """Maneja el movimiento y disparo localmente antes de enviar al servidor."""
    keys = pygame.key.get_pressed()
    accion = None
    old_y = player.y
    
    # Movimiento vertical (Carriles)
    if keys[controles['up']] and player.y > 300: 
        player.y -= 5
    if keys[controles['down']] and player.y < 550: 
        player.y += 5
    
    # Acción de disparo
    if keys[controles['shoot']]: 
        accion = "disparar"
        
    return accion, (player.y != old_y)

# --- BUCLE PRINCIPAL ---
running = True
while running:
    clock.tick(60)

    # --- 1. LÓGICA DE RED (RECEPCIÓN) ---
    while True:
        message, addr = client.receive()
        if not message: break
        
        msg_type = message.get("type")
        payload = message.get("payload")

        if msg_type == "start_game":
            try:
                # 1. Extraer variantes de castillo (Ej: "Castle 1" -> "1")
                var_a = str(payload["team_a"].get("castle", "Castle 1")).split(" ")[-1]
                var_b = str(payload["team_b"].get("castle", "Castle 2")).split(" ")[-1]
                
                # 2. Crear Jugadores con los nombres reales de personajes (War 1, Gent 2, etc.)
                # Estos nombres vienen de lo que cada cliente eligió en su StartScreen
                p1 = Player(payload["team_a"]["names"][0], "A", 160, 350)
                p2 = Player(payload["team_a"]["names"][1], "A", 160, 450)
                p3 = Player(payload["team_b"]["names"][0], "B", 845, 350)
                p4 = Player(payload["team_b"]["names"][1], "B", 845, 450)
                
                # 3. Configurar Castillos y tipos de Enemigos
                castles = {
                    "A": Castle("A", -70, 250, variant=var_a), 
                    "B": Castle("B", 840, 250, variant=var_b)
                }
                enemy_types = {
                    "A": payload["team_a"].get("enemy", "Troll 1"), 
                    "B": payload["team_b"].get("enemy", "Troll 1")
                }
                
                # 4. Inicializar Estado del Juego (Lógica)
                game_state = GameState([p1, p2, p3, p4], castles, enemy_types)
                game_state.local_players = set(mis_nombres_locales)
                
                # 5. Inicializar Pantalla de Juego (Visual)
                # Pasamos 'payload' completo para que el Renderer sepa qué enemigos cargar
                game_screen = GameScreen(screen, {
                    "players": [p1, p2, p3, p4], 
                    "castle_a": var_a, 
                    "castle_b": var_b
                })
                
                state = "game"
                print(f"🎮 Juego Iniciado: {payload['team_a']['names']} vs {payload['team_b']['names']}")
                
            except Exception as e:
                print(f"❌ Error crítico al iniciar juego: {e}")

        elif msg_type == "state_update" and game_state:
            # Aquí es donde los monstruos y otros jugadores se sincronizan
            game_state.update_from_server(payload)

    # --- 2. EVENTOS DE ENTRADA ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
            
        if state == "start":
            # handle_event devuelve True cuando el usuario pulsa "JUGAR"
            if start_screen.handle_event(event):
                # Guardamos qué personajes elegimos localmente (Ej: ["War 1", "Fairy 2"])
                mis_nombres_locales = [start_screen.player1_name, start_screen.player2_name]
                
                # Enviamos al servidor nuestra elección
                client.send_ready({
                    "names": mis_nombres_locales, 
                    "enemy": start_screen.selected_enemy, 
                    "castle": start_screen.selected_castle
                })
                state = "waiting"

    # --- 3. LÓGICA DE JUEGO (ENVÍO DE DATOS) ---
    if state == "game" and game_state:
        # Definimos controles para los dos jugadores de esta PC
        esquemas = [
            {'up': pygame.K_w, 'down': pygame.K_s, 'shoot': pygame.K_SPACE}, 
            {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'shoot': pygame.K_RETURN}
        ]
        
        datos_a_enviar = []
        hubo_cambio = False
        
        for i, nombre in enumerate(mis_nombres_locales):
            p = game_state.players.get(nombre)
            if p:
                accion, movido = procesar_input_local(p, esquemas[i])
                if movido or accion:
                    hubo_cambio = True
                    datos_a_enviar.append({
                        "name": p.name, 
                        "x": p.x, 
                        "y": p.y, 
                        "action": accion
                    })
        
        # Enviamos nuestra posición y acciones al servidor para que el resto nos vea
        if hubo_cambio: 
            client.send_update(datos_a_enviar)
        
        # El cliente puede ejecutar lógica menor (como predicción)
        game_state.update_client()

    # --- 4. DIBUJO ---
    screen.fill((0, 0, 0)) # Limpiar pantalla
    
    if state == "start": 
        start_screen.draw()
    elif state == "waiting": 
        waiting_screen.draw()
    elif state == "game" and game_screen: 
        # Renderer.render() dibuja fondo, castillos, monstruos y jugadores
        game_screen.draw(game_state)
    
    pygame.display.flip()

# --- FINALIZACIÓN ---
client.close()
pygame.quit()
sys.exit()