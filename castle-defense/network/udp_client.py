import socket
from utils.constants import SERVER_IP, SERVER_PORT, BUFFER_SIZE
from .message import parse_message, create_message


class UDPClient:
    def __init__(self, server_ip=SERVER_IP, server_port=SERVER_PORT, buffer_size=BUFFER_SIZE):
        self.server_address = (server_ip, server_port)
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.connected = False
        self.pending_messages = []

    def send(self, message_type, payload):
        data = create_message(message_type, payload)
        self.sock.sendto(data, self.server_address)

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(self.buffer_size)
        except BlockingIOError:
            return None, None

        message = parse_message(data)
        if message:
            self.pending_messages.append(message)
        return message, addr

    def send_screen_change(self, screen_state):
        self.send("screen_change", {"state": screen_state})

    def send_ready(self):
        self.send("ready", {})

    def get_pending_messages(self):
        messages = self.pending_messages[:]
        self.pending_messages.clear()
        return messages

    def close(self):
        self.sock.close()
