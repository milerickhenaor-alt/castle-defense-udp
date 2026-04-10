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
        self.sock.setblocking(False)

    def send(self, msg_type, payload):
        message = {
            "type": msg_type,
            "payload": payload
        }
        try:
            self.sock.sendto(json.dumps(message).encode(), self.server_address)
        except:
            pass

    def send_connect(self):
        self.send("connect", {})

    def send_ready(self, data):
        self.send("ready", data)

    def send_update(self, data):
        self.send("update", data)

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            return json.loads(data.decode()), addr
        except:
            return None, None