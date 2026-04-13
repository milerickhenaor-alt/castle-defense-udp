import socket
import json
import time

from model.game_state import GameState
from model.player import Player
from model.castle import Castle
from model.projectile import Projectile

class UDPServer:
    def __init__(self, host="0.0.0.0", port=5000):
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.server_address)
        self.sock.setblocking(False)

        print(f"🚀 SERVIDOR INICIADO EN PUERTO {port}")
        print("Esperando conexiones...")

        self.clients = set()
        self.ready_players = {} 
        self.game_state = None

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            message = json.loads(data.decode())
            if addr not in self.clients:
                self.clients.add(addr)
                print(f"✨ Nuevo cliente detectado: {addr}")
            return message, addr
        except:
            return None, None

    def send(self, message, addr):
        try:
            self.sock.sendto(json.dumps(message).encode(), addr)
        except Exception as e:
            print(f"❌ Error al enviar a {addr}: {e}")

    def broadcast(self, message):
        for client in self.clients:
            self.send(message, client)

    def update(self):
        # 1. PROCESAR MENSAJES
        while True:
            message, addr = self.receive()
            if message is None:
                break

            msg_type = message.get("type")
            payload = message.get("payload")

            if msg_type == "connect":
                print(f"🔗 Cliente {addr} solicitó conexión")
                self.send({"type": "connect_ack", "payload": {}}, addr)

            elif msg_type == "ready":
                self.ready_players[addr] = payload
                print(f"✅ JUGADOR LISTO: {addr}. Total listos: {len(self.ready_players)}/2")

                # INICIAR PARTIDA SI HAY 2
                if len(self.ready_players) >= 2 and not self.game_state:
                    print("🎮 ¡PARTIDA LISTA! Generando GameState...")
                    players_data = list(self.ready_players.values())

                    # Crear entidades
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

                    self.game_state = GameState([p1, p2, p3, p4], castles, enemy_types)
                    
                    start_msg = {
                        "type": "start_game",
                        "payload": {
                            "team_a": players_data[0],
                            "team_b": players_data[1]
                        }
                    }
                    print("📡 Enviando start_game a todos los clientes...")
                    self.broadcast(start_msg)

            elif msg_type == "update" and self.game_state:
                # Sincronización de movimiento y disparos
                for p_info in payload:
                    player = self.game_state.players.get(p_info["name"])
                    if player:
                        player.x = p_info["x"]
                        player.y = p_info["y"]
                        if p_info.get("action") == "shoot":
                            dx = 1 if player.team == "A" else -1

                            proyectil = Projectile(
                                owner_name=player.name,
                                team=player.team,
                                x=player.x,
                                y=player.y,
                                dx=dx,
                                dy=0
                            )

                            self.game_state.projectiles.append(proyectil)

        # 2. ACTUALIZAR FÍSICA Y NOTIFICAR ESTADO
        if self.game_state:
            self.game_state.update_server()
            self.broadcast({
                "type": "state_update",
                "payload": self.game_state.to_dict()
                
            })