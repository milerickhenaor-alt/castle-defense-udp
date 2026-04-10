import time
from network.udp_server import UDPServer
from model.game_state import GameState

server = UDPServer()
# El GameState del servidor se inicializará cuando los jugadores estén listos
# (Esto suele gestionarse dentro de UDPServer o mediante un trigger)

print("🚀 Servidor corriendo... esperando jugadores")

try:
    while True:
        # 1. Recibir paquetes y actualizar conexiones
        server.update()
        
        # 2. Si el juego ya empezó, actualizar física
        if server.game_state:
            server.game_state.update_server()
            
            # 3. Enviar el nuevo estado a todos los clientes
            payload = server.game_state.to_dict()
            server.broadcast({"type": "state_update", "payload": payload})
            
        time.sleep(0.01) # 100 FPS aprox para el servidor
except KeyboardInterrupt:
    print("\n🛑 Servidor detenido.")