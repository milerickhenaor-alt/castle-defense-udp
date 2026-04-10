import socket
import json
from utils.propertiesmanager import PropertiesManager


class UDPClient:

    def __init__(self):
        config = PropertiesManager()

        self.server_ip = config.get("server.ip")
        self.server_port = config.get_int("server.port")
        self.client_port = config.get_int("client.port", 0)

        self.server_address = (self.server_ip, self.server_port)

        print("Cliente configurado para conectar a:", self.server_address)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 🔥 IMPORTANTE: bind para recibir correctamente
        self.sock.bind(("0.0.0.0", self.client_port))

        self.sock.setblocking(False)

    # ================= ENVÍO BASE =================
    def send(self, message_type, payload):
        message = {
            "type": message_type,
            "payload": payload   # 🔥 IMPORTANTE: usas 'payload' en main
        }

        try:
            self.sock.sendto(json.dumps(message).encode(), self.server_address)
        except Exception as e:
            print("Error enviando UDP:", e)

    # ================= PROTOCOLO =================

    def send_connect(self):
        self.send("connect", {})

    def send_ready(self, data):
        self.send("ready", data)

    def send_update(self, data):
        self.send("update", data)

    def send_disconnect(self):
        self.send("disconnect", {})

    # ================= RECEPCIÓN =================
    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            message = json.loads(data.decode())

            return message, addr  # 🔥 AHORA coincide con tu main

        except BlockingIOError:
            return None, None

        except Exception as e:
            print("Error recibiendo UDP:", e)
            return None, None

    # ================= CIERRE =================
    def close(self):
        self.sock.close()