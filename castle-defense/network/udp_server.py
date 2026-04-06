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
        self.clients = set()
        self.ready_clients = set()
        self.expected_players = 2  # Asumir 2 jugadores para este juego

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(self.buffer_size)
        except BlockingIOError:
            return None, None

        message = parse_message(data)
        if message:
            self.handle_message(message, addr)
        return message, addr

    def handle_message(self, message, addr):
        msg_type = message['type']
        if msg_type == 'connect':
            self.clients.add(addr)
            # Enviar estado actual o algo, pero por ahora nada
        elif msg_type == 'ready':
            self.ready_clients.add(addr)
            if len(self.ready_clients) == self.expected_players:
                self.send_to_all('start_game', {})
                self.ready_clients.clear()  # Reset para siguiente ronda si necesario
        elif msg_type == 'screen_change':
            # Retransmitir a todos los clientes
            self.send_to_all_except('screen_change', message['payload'], addr)

    def send(self, message_type, payload, address):
        data = create_message(message_type, payload)
        self.sock.sendto(data, address)

    def send_to_all(self, message_type, payload):
        for client in self.clients:
            self.send(message_type, payload, client)

    def send_to_all_except(self, message_type, payload, exclude_addr):
        for client in self.clients:
            if client != exclude_addr:
                self.send(message_type, payload, client)

    def close(self):
        self.is_running = False
        self.sock.close()