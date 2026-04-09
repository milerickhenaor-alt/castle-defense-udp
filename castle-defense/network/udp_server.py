import socket
<<<<<<< HEAD
import json
from utils.properties_manager import PropertiesManager

class UDPServer:

    def __init__(self):
        config = PropertiesManager()

        host = config.get("server.ip")
        port = config.get_int("server.port")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.sock.setblocking(False)

        self.clients = {}

        print(f"Servidor en {host}:{port}")
=======
import time
from network.message import parse_message, create_message
from utils.constants import SERVER_IP, SERVER_PORT
from model.game_state import GameState
from model.player import Player
from model.castle import Castle

class UDPServer:
    def __init__(self, host=SERVER_IP, port=SERVER_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.sock.setblocking(False)
        
        self.clients = {}  # Diccionario {addr: team_data} para identificar quién es quién
        self.prepared_teams = [] # Lista de datos recibidos de StartScreen
        self.game_state = None
        print(f"📡 Servidor iniciado en {host}:{port}")
>>>>>>> 64dda41e35971e3a94d934d7e5c9c11ca54f8a95

    def receive(self):
        """Escucha mensajes y decide qué hacer según el tipo."""
        try:
            data, addr = self.sock.recvfrom(4096)
<<<<<<< HEAD
            msg = json.loads(data.decode())
            self.handle(msg, addr)
        except:
            pass

    def handle(self, msg, addr):
        if msg["type"] == "connect":
            self.clients[addr] = True

    def broadcast(self, msg):
        data = json.dumps(msg).encode()

        for addr in self.clients:
            try:
                self.sock.sendto(data, addr)
            except:
                pass
=======
            message = parse_message(data)
            if message:
                self.handle_message(message, addr)
        except BlockingIOError:
            pass
        except Exception as e:
            print(f"❌ Error en receive: {e}")

    def handle_message(self, message, addr):
        msg_type = message.get("type")
        payload = message.get("payload")

        # 1. Registro de jugadores (FASE WAITING)
        if msg_type == "ready":
            # Evitar registrar la misma PC dos veces si reenvía el paquete
            if addr not in self.clients:
                print(f"✅ Equipo recibido de {addr}: {payload['names']}")
                payload["addr"] = addr
                self.clients[addr] = payload
                self.prepared_teams.append(payload)

            # Si ya tenemos los 2 equipos (2 PCs), empezamos
            if len(self.prepared_teams) == 2 and self.game_state is None:
                self.start_match()

        # 2. Actualización de movimientos (FASE GAME)
        elif msg_type == "update" and self.game_state:
            # El payload es una lista de [{name, x, y, action}, ...]
            for p_data in payload:
                nombre = p_data.get("name")
                player_obj = self.game_state.players.get(nombre)
                if player_obj:
                    player_obj.y = p_data.get("y")
                    player_obj.x = p_data.get("x")
                    
                    if p_data.get("action") == "disparar":
                        # El servidor crea el proyectil en su lógica maestra
                        self.game_state.spawn_projectile(player_obj)

    def start_match(self):
        """Inicializa el GameState oficial y avisa a los clientes."""
        print("🎮 ¡Ambos equipos listos! Creando partida oficial...")
        
        team_a = self.prepared_teams[0]
        team_b = self.prepared_teams[1]

        # 1. Crear objetos del modelo en el servidor
        p1 = Player(team_a["names"][0], "A", 120, 350)
        p2 = Player(team_a["names"][1], "A", 120, 450)
        p3 = Player(team_b["names"][0], "B", 880, 350)
        p4 = Player(team_b["names"][1], "B", 880, 450)
        
        castles = {
            "A": Castle("A", -70, 250, variant=str(team_a["castle"]).split(" ")[-1]),
            "B": Castle("B", 840, 250, variant=str(team_b["castle"]).split(" ")[-1])
        }
        
        enemy_types = {"A": team_a["enemy"], "B": team_b["enemy"]}
        
        # El servidor ahora tiene el control de la lógica
        self.game_state = GameState([p1, p2, p3, p4], castles, enemy_types)

        # 2. Avisar a los clientes para que cambien a GameScreen
        start_payload = {
            "team_a": team_a,
            "team_b": team_b
        }
        msg = create_message("start_game", start_payload)
        self.broadcast(msg)

    def broadcast_state(self):
        """Envía el estado actual (Trolls, Castillos, Balas) a todos los clientes."""
        if self.game_state:
            # Convertimos el GameState a un diccionario serializable
            state_data = self.game_state.to_dict() 
            msg = create_message("state_update", state_data)
            self.broadcast(msg)

    def broadcast(self, data):
        """Envía bytes a todos los clientes conectados."""
        for addr in self.clients:
            try:
                self.sock.sendto(data, addr)
            except Exception as e:
                print(f"⚠️ Error enviando a {addr}: {e}")

    def update(self):
        if self.game_state:
            self.game_state.update_server()   # 🔥 CAMBIO CLAVE
            self.broadcast_state()
>>>>>>> 64dda41e35971e3a94d934d7e5c9c11ca54f8a95
