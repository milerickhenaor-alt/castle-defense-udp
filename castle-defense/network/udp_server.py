import socket
import json
from utils.constants import SERVER_IP, SERVER_PORT, BUFFER_SIZE
from .message import parse_message, create_message

class UDPServer:
    def __init__(self, host=SERVER_IP, port=SERVER_PORT, buffer_size=BUFFER_SIZE):
        self.address = (host, port)
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.sock.bind(self.address)
        
        self.clients = set()
        self.players_data = {} # Guarda {addr: datos_de_instancia}
        self.expected_instances = 2 

    def receive(self):
        """Este es el método que llama run_server.py"""
        try:
            data, addr = self.sock.recvfrom(self.buffer_size)
            message = parse_message(data)
            if message:
                self.handle_message(message, addr)
        except BlockingIOError:
            pass # No hay datos, seguimos adelante
        except Exception as e:
            print(f"❌ Error en recepción: {e}")

    def handle_message(self, message, addr):
        msg_type = message.get('type')
        payload = message.get('payload')

        if msg_type == 'connect':
            print(f"🔌 Nuevo cliente conectado: {addr}")
            self.clients.add(addr)

        elif msg_type == 'ready':
            print(f"✅ Instancia lista: {addr}")
            # Guardamos la formación (nombres, castillo, etc.) de esta instancia
            self.players_data[addr] = payload
            
            # Si ya tenemos las 2 instancias (4 jugadores en total)
            if len(self.players_data) == self.expected_instances:
                self.start_game()

    def start_game(self):
        print("🚀 ¡Ambos equipos listos! Enviando START_GAME...")
        addrs = list(self.players_data.keys())
        
        # Emparejamos: La primera instancia es Equipo A, la segunda Equipo B
        combined_payload = {
            "team_a": self.players_data[addrs[0]],
            "team_b": self.players_data[addrs[1]]
        }
        
        self.send_to_all('start_game', combined_payload)
        self.players_data.clear() # Limpiamos para una futura partida

    def send(self, message_type, payload, address):
        data = create_message(message_type, payload)
        self.sock.sendto(data, address)

    def send_to_all(self, message_type, payload):
        for client in self.clients:
            try:
                self.send(message_type, payload, client)
            except Exception as e:
                print(f"Error enviando a {client}: {e}")

    def close(self):
        self.sock.close()