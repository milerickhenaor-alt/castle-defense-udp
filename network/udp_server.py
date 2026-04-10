import socket
import json

class UDPServer:
    def __init__(self, host="0.0.0.0", port=5000):
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.server_address)
        self.sock.setblocking(False)

        print(f"Servidor UDP iniciado en {host}:{port}")

        self.clients = set()
        self.ready_players = {}

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            message = json.loads(data.decode())
            if addr not in self.clients:
                self.clients.add(addr)
                print(f"Nuevo cliente detectado: {addr}")
            return message, addr
        except (BlockingIOError, Exception):
            return None, None

    def send(self, message, addr):
        try:
            self.sock.sendto(json.dumps(message).encode(), addr)
        except Exception as e:
            print(f"Error enviando a {addr}: {e}")

    def broadcast(self, message):
        for client in self.clients:
            self.send(message, client)

    def update(self):
        # Procesamos todos los mensajes pendientes en el buffer
        while True:
            message, addr = self.receive()
            if message is None:
                break  # No hay más mensajes por ahora

            msg_type = message.get("type")
            payload = message.get("payload")

            if msg_type == "connect":
                print(f"Conexión establecida con: {addr}")
                self.send({"type": "connect_ack", "payload": {}}, addr)

            elif msg_type == "ready":
                self.ready_players[addr] = payload
                print(f"Jugador listo: {addr}. Total listos: {len(self.ready_players)}")

                # Iniciar partida cuando hay al menos 2 clientes (2 equipos de 2)
                if len(self.ready_players) >= 2:
                    players_data = list(self.ready_players.values())
                    start_payload = {
                        "team_a": players_data[0],
                        "team_b": players_data[1]
                    }
                    print("🚀 Condiciones cumplidas. Enviando start_game...")
                    self.broadcast({
                        "type": "start_game", 
                        "payload": start_payload
                    })

            elif msg_type == "update":
                # Reenvío de estados de juego (movimientos, disparos)
                self.broadcast({"type": "state_update", "payload": payload})