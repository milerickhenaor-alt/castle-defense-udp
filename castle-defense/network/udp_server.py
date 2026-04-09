import socket
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

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
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