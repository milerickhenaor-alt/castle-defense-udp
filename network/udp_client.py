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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Escuchar en cualquier interfaz local en el puerto configurado
        self.sock.bind(("0.0.0.0", self.client_port))
        self.sock.setblocking(False)
        print(f"Cliente UDP listo en puerto local {self.client_port}")

    def send(self, message_type, payload):
        message = {"type": message_type, "payload": payload}
        try:
            self.sock.sendto(json.dumps(message).encode(), self.server_address)
        except Exception as e:
            print(f"Error enviando UDP: {e}")

    def send_connect(self): self.send("connect", {})
    def send_ready(self, data): self.send("ready", data)
    def send_update(self, data): self.send("update", data)

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            return json.loads(data.decode()), addr
        except (BlockingIOError, Exception):
            return None, None

    def close(self):
        self.sock.close()