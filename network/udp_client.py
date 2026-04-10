"""
network/udp_client.py

Principios SOLID aplicados
--------------------------
SRP : UDPClient solo maneja la comunicación de red del cliente.
      No conoce la lógica del juego ni la interfaz gráfica.
DIP : Depende de PropertiesManager (abstracción de configuración),
      no de valores hardcodeados.
"""

import socket
import json
from utils.propertiesmanager import PropertiesManager


class UDPClient:
    """
    Cliente UDP — envía y recibe mensajes del servidor.
    SRP: responsabilidad única de comunicación de red.
    """

    def __init__(self):
        # DIP: configuración inyectada desde PropertiesManager
        config = PropertiesManager()
        self.server_ip   = config.get("server.ip")
        self.server_port = config.get_int("server.port")
        self.server_address = (self.server_ip, self.server_port)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            self.sock.bind(("", 0))
            self.sock.setblocking(False)
            puerto_asignado = self.sock.getsockname()[1]
            print(f"📡 Cliente UDP listo. Puerto local asignado: {puerto_asignado}")
            print(f"🔗 Intentando conectar al servidor en: {self.server_address}")
        except Exception as e:
            print(f"❌ Error crítico al inicializar socket cliente: {e}")

    # ------------------------------------------------------------------ #
    #  Envío de mensajes                                                   #
    # ------------------------------------------------------------------ #

    def send(self, message_type: str, payload: dict) -> None:
        """SRP: solo serializa y envía el mensaje al servidor."""
        message = {"type": message_type, "payload": payload}
        try:
            self.sock.sendto(json.dumps(message).encode(), self.server_address)
        except Exception as e:
            print(f"❌ Error enviando datos a {self.server_address}: {e}")

    def send_connect(self): self.send("connect", {})
    def send_ready(self, data): self.send("ready", data)
    def send_update(self, data): self.send("update", data)

    # ------------------------------------------------------------------ #
    #  Recepción de mensajes                                               #
    # ------------------------------------------------------------------ #

    def receive(self):
        """SRP: solo recibe y deserializa el mensaje del servidor."""
        try:
            data, addr = self.sock.recvfrom(4096)
            return json.loads(data.decode()), addr
        except (BlockingIOError, Exception):
            return None, None

    def close(self) -> None:
        """Cierra el socket al terminar la partida."""
        self.sock.close()