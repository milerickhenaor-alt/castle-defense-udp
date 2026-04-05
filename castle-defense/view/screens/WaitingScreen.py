import pygame

class WaitingScreen:
    def __init__(self, screen):
        self.screen = screen

        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 28)

        self.timer = 0

    def update(self):
        self.timer += 1

    def draw(self):
        self.screen.fill((15, 20, 30))

        # 🎯 Título
        title = self.font_title.render("Esperando conexión", True, (255, 200, 50))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 200))

        # 🔄 Animación de puntos
        dots = "." * ((self.timer // 30) % 4)
        dots_text = self.font_text.render(dots, True, (255, 255, 255))
        self.screen.blit(dots_text, (self.screen.get_width()//2 + 150, 210))

        # 💡 Info
        info = self.font_text.render("Conectando con otro jugador...", True, (200, 200, 200))
        self.screen.blit(info, (self.screen.get_width()//2 - info.get_width()//2, 300))