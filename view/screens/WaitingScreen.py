import pygame

class WaitingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 30)
        self.is_ready = False

    def handle_event(self, event):
        pass

    def update(self):
        # La lógica de recibir el mensaje ahora vive en el main.py 
        # para que el cambio de pantalla sea global y sincronizado.
        pass

    def draw(self):
        self.screen.fill((20, 20, 30)) # Un azul oscuro para que se vea mejor
        text = self.font.render("Esperando a que el otro equipo se conecte...", True, (255, 255, 255))
        # Centrado para pantalla de 1000px
        self.screen.blit(text, (280, 280))