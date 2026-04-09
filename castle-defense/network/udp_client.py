import socket
import json
from utils.constants import SERVER_IP, SERVER_PORT, BUFFER_SIZE
from .message import *

class UDPClient:
    def __init__(self, server_ip=SERVER_IP, server_port=SERVER_PORT, buffer_size=BUFFER_SIZE):
        self.server_address = (server_ip, server_port)
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)

    def send(self, msg_type, payload):
        """
        Método base de envío. Empaqueta en JSON con type y payload.
        """
        data = {
            "type": msg_type,
            "payload": payload
        }
        try:
            message = json.dumps(data).encode('utf-8')
            self.sock.sendto(message, self.server_address)
            print(f"📤 ENVIANDO: {msg_type} {payload}")
        except Exception as e:
            print(f"Error enviando socket: {e}")

    # --- Métodos de Interfaz para el Main ---

    def send_connect(self):
        self.send("connect", {})

    def send_ready(self, selections):
        """Envía nombres, tropa y castillo elegido"""
        self.send("ready", selections)

    # En udp_client.py (Agrega o actualiza este método)
    def send_update(self, players_data_list):
        """
        Envia el estado de los jugadores locales.
        players_data_list: [{'name': 'Fairy 1', 'x': 120, 'y': 400}, {...}]
        """
        payload = players_data_list
        try:
            # Usamos el tipo "update" que el servidor espera
            message = create_message("update", payload)
            self.sock.sendto(message, self.server_address)
        except Exception as e:
            print(f"Error en send_update: {e}")

    def receive(self):
        """
        Escucha mensajes del servidor. 
        Retorna (message_dict, address) o (None, None) si no hay datos.
        """
        try:
            data, addr = self.sock.recvfrom(self.buffer_size)
            message = parse_message(data)
            if message:
                print("📩 RECIBIDO:", message)
            return message, addr
        except BlockingIOError:
            return None, None
        except Exception as e:
            print(f"Error recibiendo socket: {e}")
            return None, None

    def close(self):
        self.sock.close()
