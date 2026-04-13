"""Cliente UDP no-bloqueante que se conecta al servidor del juego."""

import socket
import json
from utils.propertiesmanager import PropertiesManager

class UDPClient:
    """Cliente UDP para enviar y recibir mensajes del servidor.
    
    Gestiona: conexión al servidor, envío de actualizaciones y recepción de estado del juego.
    """
    def __init__(self):
        """Inicializa cliente UDP con configuración del servidor desde properties."""
        config = PropertiesManager()
        self.server_ip = config.get("server.ip")
        self.server_port = config.get_int("server.port")

        self.server_address = (self.server_ip, self.server_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            # Usar "" y puerto 0 permite que Windows asigne automáticamente 
            # cualquier puerto libre y escuche en todas las interfaces.
            self.sock.bind(("", 0))
            self.sock.setblocking(False)
            puerto_asignado = self.sock.getsockname()[1]
            print(f"📡 Cliente UDP listo. Puerto local asignado: {puerto_asignado}")
            print(f"🔗 Intentando conectar al servidor en: {self.server_address}")
        except Exception as e:
            print(f"❌ Error crítico al inicializar socket cliente: {e}")

    def send(self, message_type, payload):
        """Envía mensaje JSON al servidor."""
        message = {"type": message_type, "payload": payload}
        try:
            self.sock.sendto(json.dumps(message).encode(), self.server_address)
        except Exception as e:
            print(f"❌ Error enviando datos a {self.server_address}: {e}")

    def send_connect(self):
        """Envía mensaje de conexión."""
        self.send("connect", {})
    
    def send_ready(self, data):
        """Envía que está listo con datos de preparación."""
        self.send("ready", data)
    
    def send_update(self, data):
        """Envía actualización de movimiento/acciones durante la partida."""
        self.send("update", data)

    def receive(self):
        """Recibe mensaje del servidor. Retorna (mensaje, dirección) o (None, None)."""
        try:
            data, addr = self.sock.recvfrom(4096)
            return json.loads(data.decode()), addr
        except (BlockingIOError, Exception):
            return None, None

    def close(self):
        """Cierra la conexión del socket."""
        self.sock.close()
