import json
from enum import Enum


class MessageType(str, Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    INPUT = "input"
    STATE_UPDATE = "state_update"
    SPAWN_ENEMY = "spawn_enemy"
    DAMAGE_CASTLE = "damage_castle"
    GAME_OVER = "game_over"


def create_message(message_type, payload):
    """Build a JSON message ready to send over UDP."""
    packet = {
        "type": message_type,
        "payload": payload,
    }
    return json.dumps(packet).encode("utf-8")


def parse_message(data):
    """Parse incoming UDP bytes into a Python dictionary."""
    try:
        text = data.decode("utf-8")
        packet = json.loads(text)
        if "type" in packet and "payload" in packet:
            return packet
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None

    return None
