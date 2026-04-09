from network.udp_server import UDPServer
import time

server = UDPServer()

print("🚀 Server corriendo... esperando jugadores")

while True:
    server.receive()
    server.update()
    time.sleep(0.016)  # ~60 FPS