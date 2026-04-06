import socket
from utils.constants import SERVER_IP, SERVER_PORT, BUFFER_SIZE
from .message import parse_message, create_message


class UDPClient:
    def __init__(self, server_ip=SERVER_IP, server_port=SERVER_PORT, buffer_size=BUFFER_SIZE):
        self.server_address = (server_ip, server_port)
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)

    def send(self, message_type, payload):
        data = create_message(message_type, payload)
        print("📤 ENVIANDO:", message_type, payload)
        self.sock.sendto(data, self.server_address)
    
    def send_connect(self):
        self.send("connect", {})
    
    def handle_message(self, message, addr):
        print("📥 SERVER RECIBE:", message, "de", addr)

        msg_type = message['type']

        if msg_type == 'connect':
            print("🔌 Cliente conectado:", addr)
            self.clients.add(addr)

        elif msg_type == 'ready':
            print("✅ Cliente listo:", addr)
            self.ready_clients.add(addr)

            print("Clientes ready:", len(self.ready_clients))

            if len(self.ready_clients) == self.expected_players:
                print("🚀 Enviando START_GAME")
                self.send_to_all('start_game', {})
                self.ready_clients.clear()

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(self.buffer_size)
        except BlockingIOError:
            return None, None

        message = parse_message(data)

        if message:
            print("📩 RECIBIDO:", message)

        return message, addr

    # ✅ ESTE ES EL QUE TE FALTABA REALMENTE
    def send_ready(self):
        self.send("ready", {})

    def close(self):
        self.sock.close()