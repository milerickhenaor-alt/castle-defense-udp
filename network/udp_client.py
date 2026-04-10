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

    def send(self, message_type, data):
        message = {
            "type": message_type,
            "data": data
        }

        try:
            self.sock.sendto(json.dumps(message).encode(), self.server_address)
        except Exception as e:
            print("Error enviando UDP:", e)

    def receive(self):
        try:
            data, _ = self.sock.recvfrom(4096)
            return json.loads(data.decode())
        except BlockingIOError:
            return None
        except Exception as e:
            print("Error recibiendo UDP:", e)
            return None

    def close(self):
        self.sock.close()