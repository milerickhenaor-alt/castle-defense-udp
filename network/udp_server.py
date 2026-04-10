import socket
import json

class UDPServer:
    def __init__(self, host="0.0.0.0", port=5000):
        """
        Inicializa el servidor UDP.
        host: "0.0.0.0" permite escuchar en todas las interfaces (Localhost y ZeroTier).
        """
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            self.sock.bind(self.server_address)
            self.sock.setblocking(False)
            print(f"🚀 Servidor UDP Activo en puerto {port}")
        except Exception as e:
            print(f"❌ Error al iniciar el servidor: {e}")

        # Diccionario para mapear IP -> Última dirección (IP, Puerto) conocida
        # Esto permite que si un cliente cambia de puerto, sigamos enviándole datos a la IP correcta.
        self.clients = {}  
        
        # Diccionario para Jugadores Listos { "Nombre": DatosDelPayload }
        self.ready_players = {} 

    def receive(self):
        """Intenta recibir un mensaje sin bloquear el programa."""
        try:
            data, addr = self.sock.recvfrom(4096)
            message = json.loads(data.decode())
            
            # 💡 CLAVE: Actualizamos siempre el puerto para la IP que nos envía el mensaje.
            # addr[0] es la IP, addr es la tupla (IP, Puerto).
            self.clients[addr[0]] = addr 
            
            return message, addr
        except (BlockingIOError, Exception):
            return None, None

    def send(self, message, addr):
        """Envía un mensaje JSON a una dirección específica."""
        try:
            self.sock.sendto(json.dumps(message).encode(), addr)
        except Exception as e:
            print(f"❌ Error enviando a {addr}: {e}")

    def broadcast(self, message):
        """Envía un mensaje a todos los clientes registrados."""
        for addr in self.clients.values():
            self.send(message, addr)

    def update(self):
        """
        Lógica principal de procesamiento. 
        Lee todos los mensajes acumulados en el buffer y reacciona a ellos.
        """
        while True:
            message, addr = self.receive()
            if message is None:
                break

            msg_type = message.get("type")
            payload = message.get("payload")

            # --- MANEJO DE CONEXIÓN INICIAL ---
            if msg_type == "connect":
                print(f"📡 Cliente conectado desde {addr}")
                self.send({"type": "connect_ack", "payload": {}}, addr)

            # --- MANEJO DE JUGADORES LISTOS ---
            elif msg_type == "ready":
                # Usamos el nombre del jugador para evitar duplicados si reinicia el cliente
                # Se asume que payload['names'] es una lista con al menos un nombre.
                nombre_jugador = payload.get("names", ["Desconocido"])[0] 
                self.ready_players[nombre_jugador] = payload
                
                print(f"✅ [{nombre_jugador}] está listo desde {addr}")
                print(f"📢 Jugadores listos: {len(self.ready_players)} / 2")

                # Si ya hay 2 o más jugadores (o equipos) listos, iniciamos partida
                if len(self.ready_players) >= 2:
                    players_data = list(self.ready_players.values())
                    start_payload = {
                        "team_a": players_data[0],
                        "team_b": players_data[1]
                    }
                    print("🔥 ¡PARTIDA INICIADA! Enviando señales de inicio...")
                    self.broadcast({
                        "type": "start_game", 
                        "payload": start_payload
                    })

            # --- MANEJO DE ACTUALIZACIÓN DE ESTADO (MOVIMIENTO/DISPAROS) ---
            elif msg_type == "update":
                # Reenviamos el estado a todos para que vean los movimientos de los demás
                self.broadcast({
                    "type": "state_update", 
                    "payload": payload
                })
            
            # --- MANEJO DE DESCONEXIÓN ---
            elif msg_type == "disconnect":
                ip_cliente = addr[0]
                if ip_cliente in self.clients:
                    del self.clients[ip_cliente]
                print(f"🔌 Cliente {addr} desconectado.")

    def close(self):
        """Cierra el socket del servidor."""
        print("🛑 Cerrando servidor...")
        self.sock.close()