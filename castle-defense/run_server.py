from network.udp_server import UDPServer
import time

server = UDPServer()

print("🚀 Server corriendo... esperando jugadores")

while True:
    server.receive()
    time.sleep(0.01)