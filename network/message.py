"""Definición de tipos de mensajes y funciones de serialización para comunicación UDP."""

import json
from enum import Enum


class MessageType(str, Enum):
    """Tipos de mensajes utilizados en la comunicación cliente-servidor.
    
    Categorías:
      - Conexión: CONNECT, DISCONNECT
      - Sincronización: UPDATE, STATE_UPDATE
      - Eventos: SPAWN_ENEMY, DAMAGE_CASTLE, GAME_OVER, SCREEN_CHANGE
      - Partida: READY, START_GAME, WAIT_FOR_PLAYERS
    """
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
    """Serializa un mensaje a JSON codificado en UTF-8.
    
    Args:
        message_type: Tipo de mensaje (string o MessageType)
        payload: Diccionario con datos del mensaje
    
    Returns:
        bytes: Mensaje JSON codificado en UTF-8
    """
    return json.dumps({
        "type": message_type,
        "payload": payload,
    }).encode("utf-8")


def parse_message(data):
    """Deserializa un mensaje JSON recibido desde UDP.
    
    Args:
        data: Bytes crudos del socket UDP
    
    Returns:
        dict: Mensaje con estructura {"type": ..., "payload": ...} o None si es inválido
    """
    try:
        packet = json.loads(data.decode("utf-8"))
        if "type" in packet and "payload" in packet:
            return packet
    except:
        return None

    return None