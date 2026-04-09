import json
from enum import Enum


class MessageType(str, Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"

    # 🔥 ESTE ES EL IMPORTANTE
    UPDATE = "update"

    STATE_UPDATE = "state_update"
    SPAWN_ENEMY = "spawn_enemy"
    DAMAGE_CASTLE = "damage_castle"
    GAME_OVER = "game_over"
    SCREEN_CHANGE = "screen_change"
    READY = "ready"
    START_GAME = "start_game"
    WAIT_FOR_PLAYERS = "wait_for_players"


def create_message(message_type, payload):
    return json.dumps({
        "type": message_type,
        "payload": payload,
    }).encode("utf-8")


def parse_message(data):
    try:
        packet = json.loads(data.decode("utf-8"))
        if "type" in packet and "payload" in packet:
            return packet
    except:
        return None

    return None