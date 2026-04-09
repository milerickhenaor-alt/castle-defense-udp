import socket
import json
<<<<<<< HEAD
from utils.propertiesmanager import PropertiesManager
=======
from utils.constants import SERVER_IP, SERVER_PORT, BUFFER_SIZE
from .message import *
>>>>>>> 64dda41e35971e3a94d934d7e5c9c11ca54f8a95

class UDPClient:

    def __init__(self):
        config = PropertiesManager()

        self.server_ip = config.get("server.ip")
        self.server_port = config.get_int("server.port")

        self.server_address = (self.server_ip, self.server_port)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)

    def send(self, msg_type, payload):
<<<<<<< HEAD
        message = {
=======
        """
        Método base de envío. Empaqueta en JSON con type y payload.
        """
        data = {
>>>>>>> 64dda41e35971e3a94d934d7e5c9c11ca54f8a95
            "type": msg_type,
            "payload": payload
        }
        try:
<<<<<<< HEAD
            self.sock.sendto(json.dumps(message).encode(), self.server_address)
        except:
            pass
=======
            message = json.dumps(data).encode('utf-8')
            self.sock.sendto(message, self.server_address)
            print(f"📤 ENVIANDO: {msg_type} {payload}")
        except Exception as e:
            print(f"Error enviando socket: {e}")

    # --- Métodos de Interfaz para el Main ---
>>>>>>> 64dda41e35971e3a94d934d7e5c9c11ca54f8a95

    def send_connect(self):
        self.send("connect", {})

<<<<<<< HEAD
    def send_ready(self, data):
        self.send("ready", data)

    def send_update(self, data):
        self.send("update", data)
=======
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
>>>>>>> 64dda41e35971e3a94d934d7e5c9c11ca54f8a95

    def receive(self):
        """
        Escucha mensajes del servidor. 
        Retorna (message_dict, address) o (None, None) si no hay datos.
        """
        try:
<<<<<<< HEAD
            data, addr = self.sock.recvfrom(4096)
            return json.loads(data.decode()), addr
        except:
            return None, None
=======
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
>>>>>>> 64dda41e35971e3a94d934d7e5c9c11ca54f8a95
