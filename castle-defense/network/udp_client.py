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

    def send(self, message_type, payload):
        data = create_message(message_type, payload)
        self.sock.sendto(data, self.server_address)

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(self.buffer_size)
        except BlockingIOError:
            return None, None

        message = parse_message(data)
        return message, addr

    def close(self):
        self.sock.close()
