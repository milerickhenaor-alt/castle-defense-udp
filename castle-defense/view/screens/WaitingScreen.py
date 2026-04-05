import pygame

class WaitingScreen:
    def __init__(self, screen):
        self.screen = screen

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 40, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)

        self.timer = 0
        self.is_ready = False  # 🔥 IMPORTANTE (lo usa el main)

    # =========================
    # EVENTOS (aunque no haga nada)
    # =========================
    def handle_event(self, event):
        pass

    # =========================
    # UPDATE (simulación conexión)
    # =========================
    def update(self):
        self.timer += 1

        # simula conexión después de 3 segundos (180 frames)
        if self.timer > 180:
            self.is_ready = True

    # =========================
    # DRAW
    # =========================
    def draw(self, screen):
        screen.fill((15, 15, 30))

        title = self.font.render("ESPERANDO AL OTRO JUGADOR...", True, (255, 255, 255))
        info = self.small_font.render("Conectando...", True, (180, 180, 180))

        # animación de puntos
        dots = "." * ((self.timer // 30) % 4)
        dots_text = self.small_font.render(dots, True, (255, 200, 50))

        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 250))
        screen.blit(info, (screen.get_width()//2 - info.get_width()//2, 320))
        screen.blit(dots_text, (screen.get_width()//2 + 80, 320))