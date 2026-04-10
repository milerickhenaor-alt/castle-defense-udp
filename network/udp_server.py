import socket
import json


class UDPServer:

    def __init__(self, host="0.0.0.0", port=5000):
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock.bind(self.server_address)
        self.sock.setblocking(False)

        print(f"Servidor UDP escuchando en {host}:{port}")

        self.clients = set()
        self.ready_players = {}  # 🔥 jugadores listos

    # ================= RECEPCIÓN =================
    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            message = json.loads(data.decode())

            if addr not in self.clients:
                self.clients.add(addr)
                print("Nuevo cliente:", addr)

            return message, addr

        except BlockingIOError:
            return None, None
        except Exception as e:
            print("Error en servidor UDP:", e)
            return None, None

    # ================= ENVÍO =================
    def send(self, message, addr):
        try:
            self.sock.sendto(json.dumps(message).encode(), addr)
        except Exception as e:
            print("Error enviando:", e)

    def broadcast(self, message):
        for client in self.clients:
            self.send(message, client)

    # ================= UPDATE =================
    def update(self):
        message, addr = self.receive()

        if message is None:
            return

        print("Mensaje recibido:", message)

        msg_type = message.get("type")
        payload = message.get("payload")  # 🔥 CORREGIDO

        # ================= CONNECT =================
        if msg_type == "connect":
            print("Cliente conectado:", addr)

            self.send({
                "type": "connect_ack",
                "payload": {}
            }, addr)

        # ================= READY =================
        elif msg_type == "ready":
            print("Jugador listo:", payload)

            self.ready_players[addr] = payload

            # 🔥 cuando hay 2 equipos (4 jugadores)
            if len(self.ready_players) >= 2:

                players_data = list(self.ready_players.values())

                start_payload = {
                    "team_a": players_data[0],
                    "team_b": players_data[1]
                }

                print("🚀 Iniciando partida")

                self.broadcast({
                    "type": "start_game",
                    "payload": start_payload
                })

        # ================= UPDATE =================
        elif msg_type == "update":
            # 🔥 reenviar a todos
            self.broadcast({
                "type": "state_update",
                "payload": payload
            })