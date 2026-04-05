import socket
from utils.constants import SERVER_IP, SERVER_PORT, BUFFER_SIZE
from .message import parse_message, create_message


class UDPServer:
    def __init__(self, host=SERVER_IP, port=SERVER_PORT, buffer_size=BUFFER_SIZE):
        self.address = (host, port)
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.sock.bind(self.address)
        self.is_running = True

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(self.buffer_size)
        except BlockingIOError:
            return None, None

        message = parse_message(data)
        return message, addr

    def send(self, message_type, payload, address):
        data = create_message(message_type, payload)
        self.sock.sendto(data, address)

    def close(self):
        self.is_running = False
        self.sock.close()
