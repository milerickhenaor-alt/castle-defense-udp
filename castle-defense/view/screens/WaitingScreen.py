import pygame
from network.udp_client import UDPClient

class WaitingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.client = UDPClient()

        self.font = pygame.font.SysFont("Arial", 30)
        self.is_ready = False

        self.sent_ready = False

        # 🔥 CONECTARSE AL SERVER
        self.client.send_connect()
        print("🔌 Enviando CONNECT")

    def handle_event(self, event):
        pass

    def update(self):
        # enviar READY solo una vez
        if not self.sent_ready:
            print("📤 Enviando READY")
            self.client.send_ready()
            self.sent_ready = True

        # recibir mensajes
        message, _ = self.client.receive()

        if message:
            if message["type"] == "start_game":
                print("🎮 START GAME recibido")
                self.is_ready = True

    def draw(self):
        self.screen.fill((0, 0, 0))

        text = self.font.render("Esperando jugadores...", True, (255, 255, 255))
        self.screen.blit(text, (300, 250))