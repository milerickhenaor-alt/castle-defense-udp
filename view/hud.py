import pygame

class Hud:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        # Fuentes para diferentes propósitos
        self.font = pygame.font.SysFont("Arial", 20)
        self.font_big = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_hp = pygame.font.SysFont("Arial", 16, bold=True) # Fuente para el número de HP

    def draw(self, game_state):
        # 1. TIEMPO: Centrado en la parte superior
        time_left = int(game_state.remaining_time)
        time_text = self.font_big.render(f"Time: {time_left} seg", True, (255, 255, 255))
        self.screen.blit(time_text, (450, 10)) 

        # 2. REFERENCIAS DE CASTILLOS
        castle_a = game_state.castles["A"]
        castle_b = game_state.castles["B"]

        # --- CASTILLO A (Izquierda) ---
        # Definir color según la vida (Verde si > 30%, Rojo si es crítico)
        color_a = (0, 200, 0) if castle_a.hp_ratio > 0.3 else (220, 0, 0)
        # Dibujar la barra física
        self.draw_bar(20, 50, 250, 20, castle_a.hp_ratio, color_a)
        # Dibujar el indicador numérico "Vida / Total" sobre la barra
        hp_text_a = self.font_hp.render(f"HP: {int(castle_a.hp)} / {int(castle_a.max_hp)}", True, (255, 255, 255))
        self.screen.blit(hp_text_a, (20 + 125 - hp_text_a.get_width()//2, 28))

        # --- CASTILLO B (Derecha) ---
        # Color inverso o según lógica (Rojo/Naranja para el rival)
        color_b = (200, 0, 0) if castle_b.hp_ratio > 0.3 else (255, 128, 0)
        # Dibujar la barra física
        self.draw_bar(730, 50, 250, 20, castle_b.hp_ratio, color_b)
        # Dibujar el indicador numérico
        hp_text_b = self.font_hp.render(f"HP: {int(castle_b.hp)} / {int(castle_b.max_hp)}", True, (255, 255, 255))
        self.screen.blit(hp_text_b, (730 + 125 - hp_text_b.get_width()//2, 28))

        # 3. PUNTAJES (SCORES): Debajo del tiempo
        # Sumamos los puntos de los jugadores de cada equipo
        score_a = sum(p.score for p in game_state.players.values() if p.team == "A")
        score_b = sum(p.score for p in game_state.players.values() if p.team == "B")
        
        score_text = self.font_big.render(f"{score_a} - {score_b}", True, (255, 255, 255))
        # Centrado horizontalmente debajo del tiempo
        self.screen.blit(score_text, (500 - score_text.get_width()//2, 60))

    def draw_bar(self, x, y, width, height, ratio, color):
        """Dibuja una barra de progreso con fondo y borde."""
        # Fondo oscuro (la parte vacía de la barra)
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, width, height))
        
        # Borde gris claro
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, width, height), 1)
        
        # Relleno de vida (proporcional al ratio)
        if ratio > 0:
            # Aseguramos que el ratio no exceda 1.0 para no salir de la barra
            clamped_ratio = min(max(ratio, 0), 1)
            pygame.draw.rect(self.screen, color, (x, y, int(width * clamped_ratio), height))