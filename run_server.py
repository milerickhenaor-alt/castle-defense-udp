from network.udp_server import UDPServer
import time

server = UDPServer()
print("🚀 Server corriendo... esperando jugadores")

try:
    while True:
        server.update()
        # Si quisieras lógica de enemigos en el servidor, iría aquí
        time.sleep(0.01) # Pequeño respiro para el procesador
except KeyboardInterrupt:
    print("\n🛑 Servidor detenido.")