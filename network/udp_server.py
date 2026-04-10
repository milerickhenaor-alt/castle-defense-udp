import socket
import json

class UDPServer:
    def __init__(self, host="0.0.0.0", port=5000):
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.server_address)
        self.sock.setblocking(False)

        print(f"🚀 Servidor UDP en puerto {port}")
        
        
        # Mapeamos IP -> Última dirección (IP, Puerto) conocida
        self.clients = {} 
        # Mapeamos IP -> Datos del jugador
        self.ready_players = {}

    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            message = json.loads(data.decode())

            print("📩 Recibido:", message, "de", addr)  # 👈 AQUÍ

            # Actualizamos la dirección
            self.clients[addr[0]] = addr 
            return message, addr
        except:
            return None, None

    def send(self, message, addr):
        try:
            self.sock.sendto(json.dumps(message).encode(), addr)
        except:
            pass

    def broadcast(self, message):
        # Enviamos a las direcciones más recientes de cada IP conectada
        for addr in self.clients.values():
            self.send(message, addr)

    def update(self):
        while True:
            message, addr = self.receive()
            if message is None: break

            msg_type = message.get("type")
            payload = message.get("payload")

            if msg_type == "connect":
                self.send({"type": "connect_ack", "payload": {}}, addr)

            elif msg_type == "ready":
                # Guardamos por IP para evitar que el mismo PC cuente doble si cambia de puerto
                self.ready_players[addr[0]] = payload
                print(f"✅ Listo: {addr[0]} | Total: {len(self.ready_players)}/2")

                if len(self.ready_players) >= 2:
                    p_list = list(self.ready_players.values())
                    start_data = {"team_a": p_list[0], "team_b": p_list[1]}
                    print("🎮 ¡INICIANDO JUEGO!")
                    self.broadcast({"type": "start_game", "payload": start_data})

            elif msg_type == "update":
                self.broadcast({"type": "state_update", "payload": payload})

