import socket
import json
import time

from model.game_state import GameState
from model.player import Player
from model.castle import Castle

class UDPServer:
    def __init__(self, host="0.0.0.0", port=5000):
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.server_address)
        self.sock.setblocking(False)

        print(f"🚀 Servidor UDP iniciado en puerto {port}")

        self.clients = set()
        self.ready_players = {}

        # 🔥 GAME STATE DEL SERVIDOR
        self.game_state = None

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            message = json.loads(data.decode())
            if addr not in self.clients:
                self.clients.add(addr)
                print(f"✨ Nuevo cliente: {addr}")
            return message, addr
        except:
            return None, None

    def send(self, message, addr):
        try:
            self.sock.sendto(json.dumps(message).encode(), addr)
        except Exception as e:
            print(f"❌ Error enviando: {e}")

    def broadcast(self, message):
        for client in self.clients:
            self.send(message, client)

    def update(self):
        # 🔥 1. RECIBIR MENSAJES
        while True:
            message, addr = self.receive()
            if message is None:
                break

            msg_type = message.get("type")
            payload = message.get("payload")

            if msg_type == "connect":
                self.send({"type": "connect_ack", "payload": {}}, addr)

            elif msg_type == "ready":
                self.ready_players[addr] = payload
                print(f"✅ Jugador listo: {len(self.ready_players)}")

                if len(self.ready_players) >= 2:
                    players_data = list(self.ready_players.values())

                    start_payload = {
                        "team_a": players_data[0],
                        "team_b": players_data[1]
                    }

                    # 🔥 CREAR GAMESTATE EN SERVIDOR
                    p1 = Player(players_data[0]["names"][0], "A", 160, 350)
                    p2 = Player(players_data[0]["names"][1], "A", 160, 450)
                    p3 = Player(players_data[1]["names"][0], "B", 845, 350)
                    p4 = Player(players_data[1]["names"][1], "B", 845, 450)

                    castles = {
                        "A": Castle("A", -70, 250),
                        "B": Castle("B", 840, 250)
                    }

                    enemy_types = {
                        "A": players_data[0].get("enemy", "Troll 1"),
                        "B": players_data[1].get("enemy", "Troll 1")
                    }

                    self.game_state = GameState(
                        [p1, p2, p3, p4],
                        castles,
                        enemy_types
                    )

                    print("🎮 Juego iniciado en servidor")

                    self.broadcast({"type": "start_game", "payload": start_payload})

            elif msg_type == "update" and self.game_state:
                # Actualizar jugadores en servidor
                for p in payload:
                    player = self.game_state.players.get(p["name"])
                    if player:
                        player.x = p["x"]
                        player.y = p["y"]

        # 🔥 2. LÓGICA DEL JUEGO (AQUÍ ESTÁ TODO)
        if self.game_state:
            self.game_state.update_server()

            # 🔥 3. ENVIAR ESTADO COMPLETO
            state = self.game_state.to_dict()
            self.broadcast({
                "type": "state_update",
                "payload": state
            })