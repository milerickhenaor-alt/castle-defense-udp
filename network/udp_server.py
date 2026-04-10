import socket
import json

class UDPServer:
    def __init__(self, host="0.0.0.0", port=5000):
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Al usar 0.0.0.0 el servidor escucha tanto en localhost como en la IP de ZeroTier
        self.sock.bind(self.server_address)
        self.sock.setblocking(False)

        print(f"🚀 Servidor UDP iniciado y escuchando en puerto {port}")
        print(f"📢 IMPORTANTE: Los clientes deben conectarse a la IP de ZeroTier de este PC.")

        self.clients = set()
        self.ready_players = {}

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            message = json.loads(data.decode())
            if addr not in self.clients:
                self.clients.add(addr)
                print(f"✨ Nuevo cliente conectado desde: {addr}")
            return message, addr
        except (BlockingIOError, Exception):
            return None, None

    def send(self, message, addr):
        try:
            self.sock.sendto(json.dumps(message).encode(), addr)
        except Exception as e:
            print(f"❌ Error enviando a {addr}: {e}")

    def broadcast(self, message):
        for client in self.clients:
            self.send(message, client)

    def update(self):
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
                print(f"✅ Jugador listo: {addr}. Total listos: {len(self.ready_players)}")

                if len(self.ready_players) >= 2:
                    players_data = list(self.ready_players.values())
                    start_payload = {
                        "team_a": players_data[0],
                        "team_b": players_data[1]
                    }
                    print("🎮 ¡Partida completa! Enviando señal de inicio...")
                    self.broadcast({"type": "start_game", "payload": start_payload})

            elif msg_type == "update":
                self.broadcast({"type": "state_update", "payload": payload})