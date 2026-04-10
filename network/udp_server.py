import socket
import json


class UDPServer:

    def __init__(self, host="0.0.0.0", port=5000):
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock.bind(self.server_address)
        self.sock.setblocking(False)

        print(f"Servidor UDP escuchando en {host}:{port}")

        self.clients = set()

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)

            message = json.loads(data.decode())

            # Registrar cliente automáticamente
            if addr not in self.clients:
                self.clients.add(addr)
                print("Nuevo cliente conectado:", addr)

            return message, addr

        except BlockingIOError:
            return None, None
        except Exception as e:
            print("Error en servidor UDP:", e)
            return None, None

    def send(self, message, addr):
        try:
            self.sock.sendto(json.dumps(message).encode(), addr)
        except Exception as e:
            print("Error enviando a cliente:", e)

    def broadcast(self, message):
        for client in self.clients:
            self.send(message, client)