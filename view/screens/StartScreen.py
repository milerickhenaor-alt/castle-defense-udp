import pygame
import os

# Configuración de ruta base
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class StartScreen:
    def __init__(self, screen):
        self.screen = screen

        pygame.mixer.init()

        # 🎨 COLORES
        self.COLOR_CARD = (45, 52, 71)
        self.COLOR_ACCENT = (255, 200, 50)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        # 🔤 FUENTES
        self.font_title = pygame.font.SysFont("Arial", 42, bold=True)
        self.font_name = pygame.font.SysFont("Arial", 24)
        self.font_rules = pygame.font.SysFont("Arial", 20)

        # 🎵 SONIDOS
        try:
            self.sound_move = pygame.mixer.Sound(os.path.join(BASE_PATH, "assets", "sounds", "move.mp3"))
            self.sound_select = pygame.mixer.Sound(os.path.join(BASE_PATH, "assets", "sounds", "select.mp3"))
        except:
            print("⚠️ Advertencia: No se encontraron algunos sonidos.")

        # 🖼️ FONDO
        bg_path = os.path.join(BASE_PATH, "assets", "images", "background", "menu.png")
        try:
            self.background = pygame.image.load(bg_path)
            self.background = pygame.transform.scale(self.background, (1000, 600))
        except:
            self.background = pygame.Surface((1000, 600))
            self.background.fill((30, 30, 60))

        # 🎮 ESTADO
        self.mode = "name"
        self.player1_name = ""
        self.player2_name = ""
        self.input_active = 1
        self.show_rules = False # Control del modal de reglas

        # 🎯 SELECCIONES
        self.avatar_index = 0
        self.troll_index = 0
        self.castle_index = 0

        self.selected_players = []
        self.selected_enemy = None
        self.selected_castle = None

        # 🧠 SCROLL E INTERFAZ
        self.scroll_offset = 0
        self.card_width = 220
        self.visible_cards = 4
        self.info_btn_rect = pygame.Rect(930, 20, 50, 50)

        # 🎭 DATOS
        self.avatars = ["Fairy 1", "Fairy 2", "Fairy 3", "Gent 1", "Gent 2", "Gent 3", "War 1", "War 2", "War 3"]
        self.trolls = ["Troll 1", "Troll 2", "Troll 3"]
        self.castles = ["Castle 1", "Castle 2", "Castle 3"]

        # 🖼️ CARGA DE IMÁGENES
        self.avatar_images = self._load_images("players", [
            "Fairies1.png","Fairies2.png","Fairies3.png",
            "gentlemen1.png","gentlemen2.png","gentlemen3.png",
            "Warrior1.png","Warrior2.png","Warrior3.png"
        ], (140, 140))

        self.troll_images = self._load_images("enemies", ["trolls1.png","trolls2.png","trolls3.png"], (140, 140))
        self.castle_images = self._load_images("castles", ["full1.png","full2.png","full3.png"], (150, 120))

    # ========================
    # 🎮 EVENTOS
    # ========================
    def handle_event(self, event):
        # Manejo de clic en el botón de Información
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.info_btn_rect.collidepoint(event.pos):
                self.show_rules = not self.show_rules
                try: self.sound_select.play() 
                except: pass
                return False
            
            # Si el modal está abierto, cualquier clic fuera lo cierra
            if self.show_rules:
                self.show_rules = False
                return False

        if event.type == pygame.KEYDOWN:
            # Si las reglas están abiertas, cualquier tecla las cierra
            if self.show_rules:
                self.show_rules = False
                return False

            if self.mode == "name":
                if event.key == pygame.K_RETURN:
                    if self.input_active == 1 and self.player1_name:
                        self.input_active = 2
                    elif self.input_active == 2 and self.player2_name:
                        self.mode = "players"
                        try: self.sound_select.play()
                        except: pass

                elif event.key == pygame.K_BACKSPACE:
                    if self.input_active == 1:
                        self.player1_name = self.player1_name[:-1]
                    else:
                        self.player2_name = self.player2_name[:-1]
                else:
                    if event.unicode.isalnum() or event.unicode == " ":
                        if self.input_active == 1:
                            self.player1_name += event.unicode
                        else:
                            self.player2_name += event.unicode

            elif self.mode == "players":
                self._handle_selection(event, self.avatars, "enemy")

            elif self.mode == "enemy":
                self._handle_selection(event, self.trolls, "castle", enemy=True)

            elif self.mode == "castle":
                finished = self._handle_selection(event, self.castles, None, castle=True)
                if finished:
                    return True
        return False

    def _handle_selection(self, event, data, next_mode, enemy=False, castle=False):
        index_attr = "avatar_index" if not enemy and not castle else \
                     "troll_index" if enemy else "castle_index"

        current_index = getattr(self, index_attr)
        use_scroll = not enemy and not castle

        if event.key == pygame.K_LEFT:
            if current_index > 0:
                setattr(self, index_attr, current_index - 1)
                if use_scroll and (current_index - 1) < abs(self.scroll_offset // self.card_width):
                    self.scroll_offset += self.card_width
                try: self.sound_move.play()
                except: pass

        elif event.key == pygame.K_RIGHT:
            if current_index < len(data) - 1:
                setattr(self, index_attr, current_index + 1)
                if use_scroll:
                    right_limit = abs(self.scroll_offset // self.card_width) + self.visible_cards - 1
                    if (current_index + 1) > right_limit:
                        self.scroll_offset -= self.card_width
                try: self.sound_move.play()
                except: pass

        elif event.key == pygame.K_RETURN:
            try: self.sound_select.play()
            except: pass
            if not enemy and not castle:
                self.selected_players.append(self.avatars[self.avatar_index])
                if len(self.selected_players) == 2:
                    self.mode = next_mode
            elif enemy:
                self.selected_enemy = self.trolls[self.troll_index]
                self.mode = next_mode
            elif castle:
                self.selected_castle = self.castles[self.castle_index]
                return True
        return False

    # ========================
    # 🎨 RENDERIZADO
    # ========================
    def draw(self):
        self.screen.blit(self.background, (0, 0))

        if self.mode == "name":
            self._draw_title("REGISTRO DE GUERREROS")
            self._draw_controls("Escribe nombre | ENTER continuar")
            self._draw_input(250, f"P1: {self.player1_name}", self.input_active == 1)
            self._draw_input(330, f"P2: {self.player2_name}", self.input_active == 2)

        elif self.mode == "players":
            self._draw_title(f"SELECCIONA JUGADOR {len(self.selected_players)+1}")
            self._draw_controls("← → mover | ENTER seleccionar")
            self._draw_grid(self.avatars, self.avatar_index, self.avatar_images)

        elif self.mode == "enemy":
            self._draw_title("ELIGE TU TROPA")
            self._draw_controls("← → mover | ENTER seleccionar")
            self._draw_grid(self.trolls, self.troll_index, self.troll_images)

        elif self.mode == "castle":
            self._draw_title("ELIGE CASTILLO")
            self._draw_controls("← → mover | ENTER seleccionar")
            self._draw_grid(self.castles, self.castle_index, self.castle_images)

        # ℹ️ Botón de Información
        pygame.draw.ellipse(self.screen, self.COLOR_ACCENT, self.info_btn_rect)
        btn_txt = self.font_name.render("i", True, self.COLOR_CARD)
        self.screen.blit(btn_txt, (self.info_btn_rect.centerx - 5, self.info_btn_rect.centery - 12))

        # 📜 Modal de Reglas
        if self.show_rules:
            self._draw_rules_modal()


    def _draw_rules_modal(self):
        # 1. Capa de fondo oscura (overlay)
        overlay = pygame.Surface((1000, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210)) 
        self.screen.blit(overlay, (0, 0))

        # 2. Caja del modal (800x520 es un buen tamaño para 1000x600)
        modal_rect = pygame.Rect(100, 40, 800, 520)
        pygame.draw.rect(self.screen, self.COLOR_CARD, modal_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.COLOR_ACCENT, modal_rect, 3, border_radius=15)

        # 3. Fuente más pequeña para el contenido (Tamaño 17)
        font_rules_small = pygame.font.SysFont("Arial", 17)
        font_credits = pygame.font.SysFont("Arial", 15)

        # 4. Título Principal
        title = self.font_title.render("REGLAS DEL JUEGO", True, self.COLOR_ACCENT)
        self.screen.blit(title, (modal_rect.centerx - title.get_width()//2, 60))

        # 5. Texto exacto del póster
        reglas = [
            "• Cada equipo debe proteger su castillo. Si la vida del castillo",
            "  llega a 0, el equipo pierde automáticamente.",
            "• Cada equipo está compuesto por 2 jugadores, que pueden",
            "  moverse verticalmente y disparar para defender.",
            "• Los enemigos aparecen automáticamente y avanzan hacia el",
            "  castillo rival. Si llegan, hacen daño continuo.",
            "• Los jugadores ganan puntos al eliminar enemigos. Estos puntos",
            "  se suman para determinar el ganador si el tiempo se acaba.",
            "",
            "EL JUEGO TERMINA CUANDO:",
            "» Un castillo es destruido → gana el equipo contrario",
            "» Se acaba el tiempo → gana el equipo con más puntos",
            "» Si hay empate → empate"
        ]

        y_text = 125
        for linea in reglas:
            # Color acento para el título de la sección y las condiciones finales
            color = self.COLOR_ACCENT if "TERMINA" in linea or "»" in linea else self.WHITE
            txt_surf = font_rules_small.render(linea, True, color)
            self.screen.blit(txt_surf, (150, y_text))
            y_text += 25 # Espaciado reducido para que no se salga

        # 6. Créditos (Pie del modal con letra aún más pequeña)
        footer_y = 485
        creditos_nombres = "Sofía Rubio Castañeda | Milerick Henao Román | Ethan Jacobo López | Johan Javier Rondón"
        u_info = "Ingeniería de Software II - Universidad Autónoma de Manizales"
        
        txt_nombres = font_credits.render(creditos_nombres, True, (180, 180, 180))
        txt_u = font_credits.render(u_info, True, self.COLOR_ACCENT)
        
        self.screen.blit(txt_nombres, (modal_rect.centerx - txt_nombres.get_width()//2, footer_y))
        self.screen.blit(txt_u, (modal_rect.centerx - txt_u.get_width()//2, footer_y + 20))
        
    def _draw_title(self, text):
        surf = self.font_title.render(text, True, self.COLOR_ACCENT)
        self.screen.blit(surf, (self.screen.get_width()//2 - surf.get_width()//2, 80))

    def _draw_controls(self, text):
        surf = self.font_name.render(text, True, (200, 200, 200))
        self.screen.blit(surf, (self.screen.get_width()//2 - surf.get_width()//2, 140))

    def _draw_input(self, y, text, active):
        color = self.COLOR_ACCENT if active else self.COLOR_CARD
        pygame.draw.rect(self.screen, color, (300, y, 400, 50), 2, border_radius=10)
        txt = self.font_name.render(text, True, self.WHITE)
        self.screen.blit(txt, (320, y + 10))

    def _draw_grid(self, items, selected, images):
        is_fixed = len(items) <= 3
        start_x = 200 if is_fixed else 120 + self.scroll_offset

        for i, item in enumerate(items):
            x = start_x + i * self.card_width
            y = 220
            rect = pygame.Rect(x, y, 180, 160)
            
            pygame.draw.rect(self.screen, (0, 0, 0), rect.move(5, 5), border_radius=12)
            pygame.draw.rect(self.screen, self.COLOR_CARD, rect, border_radius=12)

            if i == selected:
                pygame.draw.rect(self.screen, self.COLOR_ACCENT, rect, 3, border_radius=12)
                img = pygame.transform.scale(images[i], (160, 160))
            else:
                img = images[i]

            img_rect = img.get_rect(center=(x + 90, y + 70))
            self.screen.blit(img, img_rect)

            txt = self.font_name.render(item, True, self.WHITE)
            self.screen.blit(txt, (x + 90 - txt.get_width()//2, y + 165))

    def _load_images(self, folder, files, size):
        images = []
        for file in files:
            path = os.path.join(BASE_PATH, "assets", "images", folder, file)
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, size)
                images.append(img)
            except:
                surface = pygame.Surface(size)
                surface.fill((100, 100, 100))
                images.append(surface)
        return images