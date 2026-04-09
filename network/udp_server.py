import socket
import json
import time
from model.game_state import GameState
from model.player import Player
from model.castle import Castle

class UDPServer:

    def __init__(self, host="0.0.0.0", port=5000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.sock.setblocking(False)

        self.clients = {}
        self.teams = []

        self.game_state = None

        print(f"📡 Server running on {host}:{port}")

    # ================= RECEIVE =================
    def receive(self):
        try:
            data, addr = self.sock.recvfrom(4096)
            msg = json.loads(data.decode())
            self.handle_message(msg, addr)
        except:
            pass

    # ================= HANDLE =================
    def handle_message(self, msg, addr):
        msg_type = msg.get("type")
        payload = msg.get("payload")

        if msg_type == "connect":
            self.clients[addr] = True

        elif msg_type == "ready":
            payload["addr"] = addr
            self.teams.append(payload)

            if len(self.teams) == 2:
                self.start_game()

        elif msg_type == "update" and self.game_state:
            for p in payload:
                player = self.game_state.players.get(p["name"])
                if player:
                    player.x = float(p["x"])
                    player.y = float(p["y"])

    # ================= START =================
    def start_game(self):
        team_a = self.teams[0]
        team_b = self.teams[1]

        p1 = Player(team_a["names"][0], "A", 120, 350)
        p2 = Player(team_a["names"][1], "A", 120, 450)
        p3 = Player(team_b["names"][0], "B", 880, 350)
        p4 = Player(team_b["names"][1], "B", 880, 450)

        castles = {
            "A": Castle("A", -70, 250),
            "B": Castle("B", 840, 250)
        }

        self.game_state = GameState(
            [p1, p2, p3, p4],
            castles,
            {"A": team_a["enemy"], "B": team_b["enemy"]}
        )

        msg = {
            "type": "start_game",
            "payload": {
                "team_a": team_a,
                "team_b": team_b
            }
        }

        self.broadcast(msg)

    # ================= UPDATE =================
    def update(self):
        if not self.game_state:
            return

        self.game_state.update_server()

        state = {
            "type": "state_update",
            "payload": self.game_state.to_dict()
        }

        self.broadcast(state)

    # ================= SEND =================
    def broadcast(self, msg):
        data = json.dumps(msg).encode()
        for addr in self.clients:
            try:
                self.sock.sendto(data, addr)
            except:
                pass