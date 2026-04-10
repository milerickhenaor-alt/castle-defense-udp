import socket
import json
from utils.propertiesmanager import PropertiesManager

class UDPClient:
    def __init__(self):
        config = PropertiesManager()
        self.server_ip = config.get("server.ip")
        self.server_port = config.get_int("server.port")
        self.server_address = (self.server_ip, self.server_port)
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", 0)) # Puerto aleatorio
        self.sock.setblocking(False)
        print(f"📡 Cliente en puerto: {self.sock.getsockname()[1]}")

    def send(self, message_type, payload):
        msg = {"type": message_type, "payload": payload}
        try:
            self.sock.sendto(json.dumps(msg).encode(), self.server_address)
        except Exception as e:
            print(f"❌ Error envío: {e}")

    def send_connect(self): self.send("connect", {})
    def send_ready(self, data): self.send("ready", data)
    def send_update(self, data): self.send("update", data)

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            return json.loads(data.decode()), addr
        except:
            return None, None