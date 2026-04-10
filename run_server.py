import time
from network.udp_server import UDPServer

server = UDPServer()

print("🚀 Servidor corriendo... esperando jugadores")

try:
    while True:
        # El método update() ya recibe mensajes, actualiza física 
        # y hace el broadcast del estado. No necesitas nada más aquí.
        server.update()
        
        time.sleep(0.01) # 100 FPS
except KeyboardInterrupt:
    print("\n🛑 Servidor detenido.")