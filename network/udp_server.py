"""
network/udp_server.py

Principios SOLID aplicados
--------------------------
SRP : UDPServer maneja la comunicación de red y la lógica del juego
      en el servidor. El GameState se encarga de las reglas — el servidor
      solo lo llama y reenvía el resultado.
OCP : Agregar un nuevo tipo de mensaje (ej: "chat") solo requiere
      agregar un elif en update(). No se modifica la estructura existente.
DIP : UDPServer depende de GameState (abstracción del modelo),
      no de la lógica concreta del juego.
"""

import socket
import json
import time

from model.game_state import GameState
from model.player import Player
from model.castle import Castle


class UDPServer:
    """
    Servidor UDP — recibe mensajes de los clientes, ejecuta la lógica
    del juego y broadcast el estado a todos los clientes.
    SRP: coordinador de red y estado del juego en el servidor.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.server_address)
        self.sock.setblocking(False)

        print(f"🚀 Servidor UDP iniciado en puerto {port}")

        self.clients: set = set()
        self.ready_players: dict = {}

        # DIP: GameState es la única fuente de verdad del juego
        self.game_state: GameState = None

    # ------------------------------------------------------------------ #
    #  Red                                                                 #
    # ------------------------------------------------------------------ #

    def receive(self):
        """SRP: solo recibe y deserializa mensajes UDP."""
        try:
            data, addr = self.sock.recvfrom(4096)
            message = json.loads(data.decode())
            if addr not in self.clients:
                self.clients.add(addr)
                print(f"✨ Nuevo cliente: {addr}")
            return message, addr
        except:
            return None, None

    def send(self, message: dict, addr) -> None:
        """SRP: solo serializa y envía un mensaje a una dirección."""
        try:
            self.sock.sendto(json.dumps(message).encode(), addr)
        except Exception as e:
            print(f"❌ Error enviando: {e}")

    def broadcast(self, message: dict) -> None:
        """Envía un mensaje a todos los clientes conectados."""
        for client in self.clients:
            self.send(message, client)

    # ------------------------------------------------------------------ #
    #  Loop principal                                                      #
    # ------------------------------------------------------------------ #

    def update(self) -> None:
        """
        Ciclo principal del servidor:
          1. Recibir mensajes
          2. Ejecutar lógica del juego (delegada a GameState)
          3. Broadcast del estado a todos los clientes

        OCP: agregar un nuevo tipo de mensaje no modifica esta estructura.
        """
        # 1. RECIBIR MENSAJES
        while True:
            message, addr = self.receive()
            if message is None:
                break

            msg_type = message.get("type")
            payload  = message.get("payload")

            if msg_type == "connect":
                self.send({"type": "connect_ack", "payload": {}}, addr)

            elif msg_type == "ready":
                self._handle_ready(addr, payload)

            elif msg_type == "update" and self.game_state:
                self._handle_update(payload)

        # 2. LÓGICA DEL JUEGO (delegada al GameState — DIP)
        if self.game_state:
            self.game_state.update_server()

            # 3. BROADCAST DEL ESTADO
            self.broadcast({
                "type": "state_update",
                "payload": self.game_state.to_dict()
            })

    # ------------------------------------------------------------------ #
    #  Handlers privados (SRP: cada mensaje tiene su handler)             #
    # ------------------------------------------------------------------ #

    def _handle_ready(self, addr, payload: dict) -> None:
        """
        SRP: maneja exclusivamente el mensaje 'ready'.
        Cuando hay 2 jugadores listos, inicia el juego.
        """
        self.ready_players[addr] = payload
        print(f"✅ Jugador listo: {len(self.ready_players)}")

        if len(self.ready_players) >= 2:
            players_data = list(self.ready_players.values())

            start_payload = {
                "team_a": players_data[0],
                "team_b": players_data[1]
            }

            # Crear GameState en el servidor (fuente de verdad)
            p1 = Player(players_data[0]["names"][0], "A", 160, 350)
            p2 = Player(players_data[0]["names"][1], "A", 160, 450)
            p3 = Player(players_data[1]["names"][0], "B", 845, 350)
            p4 = Player(players_data[1]["names"][1], "B", 845, 450)

            castles = {
                "A": Castle("A", -70, 250),
                "B": Castle("B", 840, 250)
            }

            enemy_types = {
                "A": players_data[0].get("enemy", "Troll 1"),
                "B": players_data[1].get("enemy", "Troll 1")
            }

            self.game_state = GameState([p1, p2, p3, p4], castles, enemy_types)
            print("🎮 Juego iniciado en servidor")

            self.broadcast({"type": "start_game", "payload": start_payload})

    def _handle_update(self, payload) -> None:
        """
        SRP: maneja exclusivamente el mensaje 'update'.
        Actualiza las posiciones de los jugadores en el GameState del servidor.
        """
        if not self.game_state:
            return
        for p in payload:
            player = self.game_state.players.get(p["name"])
            if player:
                player.x = p["x"]
                player.y = p["y"]