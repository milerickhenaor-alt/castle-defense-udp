import pygame
import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class StartScreen:
    def __init__(self):
        pygame.mixer.init()

        # 🎨 COLORES
        self.COLOR_CARD = (45, 52, 71)
        self.COLOR_ACCENT = (255, 200, 50)
        self.WHITE = (255, 255, 255)

        # 🔤 FUENTES
        self.font_title = pygame.font.SysFont("Arial", 42, bold=True)
        self.font_name = pygame.font.SysFont("Arial", 24)

        # 🎵 SONIDOS (MP3)
        self.sound_move = pygame.mixer.Sound(os.path.join(BASE_PATH, "assets", "sounds", "move.mp3"))
        self.sound_select = pygame.mixer.Sound(os.path.join(BASE_PATH, "assets", "sounds", "select.mp3"))

        # 🖼️ FONDO
        bg_path = os.path.join(BASE_PATH, "assets", "images", "background", "menu.png")
        self.background = pygame.image.load(bg_path)
        self.background = pygame.transform.scale(self.background, (1000, 600))

        # 🎮 ESTADO
        self.mode = "name"
        self.player1_name = ""
        self.player2_name = ""
        self.input_active = 1

        # 🎯 SELECCIONES
        self.avatar_index = 0
        self.troll_index = 0
        self.castle_index = 0

        self.selected_players = []
        self.selected_enemy = None
        self.selected_castle = None

        # 🧠 SCROLL CONTROLADO
        self.scroll_offset = 0
        self.card_width = 220
        self.visible_cards = 4

        # 🎭 DATOS
        self.avatars = ["Fairy 1", "Fairy 2", "Fairy 3", "Gent 1", "Gent 2", "Gent 3", "War 1", "War 2", "War 3"]
        self.trolls = ["Troll 1", "Troll 2", "Troll 3"]
        self.castles = ["Castle 1", "Castle 2", "Castle 3"]

        # 🖼️ IMÁGENES
        self.avatar_images = self._load_images("players", [
            "Fairies1.png","Fairies2.png","Fairies3.png",
            "gentlemen1.png","gentlemen2.png","gentlemen3.png",
            "Warrior1.png","Warrior2.png","Warrior3.png"
        ], (140, 140))

        self.troll_images = self._load_images("enemies", [
            "trolls1.png","trolls2.png","trolls3.png"
        ], (140, 140))

        self.castle_images = self._load_images("castles", [
            "full1.png","full2.png","full3.png"
        ], (150, 120))


    # ========================
    # 🎮 EVENTOS
    # ========================
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if self.mode == "name":
                if event.key == pygame.K_RETURN:
                    if self.input_active == 1 and self.player1_name:
                        self.input_active = 2
                    elif self.input_active == 2 and self.player2_name:
                        self.mode = "players"
                        self.sound_select.play()

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

                if use_scroll:
                    if (current_index - 1) < abs(self.scroll_offset // self.card_width):
                        self.scroll_offset += self.card_width

                self.sound_move.play()

        elif event.key == pygame.K_RIGHT:
            if current_index < len(data) - 1:
                setattr(self, index_attr, current_index + 1)

                if use_scroll:
                    right_limit = abs(self.scroll_offset // self.card_width) + self.visible_cards - 1
                    if (current_index + 1) > right_limit:
                        self.scroll_offset -= self.card_width

                self.sound_move.play()

        elif event.key == pygame.K_RETURN:
            self.sound_select.play()

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


    # ========================
    # 🎨 RENDER
    # ========================
    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        if self.mode == "name":
            self._draw_title(screen, "REGISTRO DE GUERREROS")
            self._draw_controls(screen, "Escribe nombre | ENTER continuar")
            self._draw_input(screen, 250, f"P1: {self.player1_name}", self.input_active == 1)
            self._draw_input(screen, 330, f"P2: {self.player2_name}", self.input_active == 2)

        elif self.mode == "players":
            self._draw_title(screen, f"SELECCIONA JUGADOR {len(self.selected_players)+1}")
            self._draw_controls(screen, "← → mover | ENTER seleccionar")
            self._draw_grid(screen, self.avatars, self.avatar_index, self.avatar_images)

        elif self.mode == "enemy":
            self._draw_title(screen, "ELIGE TU TROPA")
            self._draw_controls(screen, "← → mover | ENTER seleccionar")
            self._draw_grid(screen, self.trolls, self.troll_index, self.troll_images)

        elif self.mode == "castle":
            self._draw_title(screen, "ELIGE CASTILLO")
            self._draw_controls(screen, "← → mover | ENTER seleccionar")
            self._draw_grid(screen, self.castles, self.castle_index, self.castle_images)


    def _draw_title(self, screen, text):
        surf = self.font_title.render(text, True, self.COLOR_ACCENT)
        screen.blit(surf, (screen.get_width()//2 - surf.get_width()//2, 80))


    def _draw_controls(self, screen, text):
        surf = self.font_name.render(text, True, (200, 200, 200))
        screen.blit(surf, (screen.get_width()//2 - surf.get_width()//2, 140))


    def _draw_input(self, screen, y, text, active):
        color = self.COLOR_ACCENT if active else self.COLOR_CARD
        pygame.draw.rect(screen, color, (300, y, 400, 50), 2, border_radius=10)
        txt = self.font_name.render(text, True, self.WHITE)
        screen.blit(txt, (320, y + 10))


    def _draw_grid(self, screen, items, selected, images):

        is_fixed = len(items) <= 3
        start_x = 200 if is_fixed else 120 + self.scroll_offset

        for i, item in enumerate(items):
            x = start_x + i * self.card_width
            y = 220

            rect = pygame.Rect(x, y, 180, 160)

            # sombra
            pygame.draw.rect(screen, (0, 0, 0), rect.move(5, 5), border_radius=12)

            pygame.draw.rect(screen, self.COLOR_CARD, rect, border_radius=12)

            if i == selected:
                pygame.draw.rect(screen, self.COLOR_ACCENT, rect, 3, border_radius=12)

                glow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                glow.fill((255, 255, 100, 40))
                screen.blit(glow, rect.topleft)

                img = pygame.transform.scale(images[i], (160, 160))
            else:
                img = images[i]

            img_rect = img.get_rect(center=(x + 90, y + 70))
            screen.blit(img, img_rect)

            # TEXTO DEBAJO
            txt = self.font_name.render(item, True, self.WHITE)
            text_x = x + rect.width // 2 - txt.get_width() // 2
            text_y = y + rect.height + 5
            screen.blit(txt, (text_x, text_y))


    # ========================
    # 🖼️ CARGA IMÁGENES
    # ========================
    def _load_images(self, folder, files, size):
        images = []
        for file in files:
            path = os.path.join(BASE_PATH, "assets", "images", folder, file)
            try:
                img = pygame.image.load(path)
                img = pygame.transform.scale(img, size)
                images.append(img)
            except:
                print("❌ Error cargando:", path)
        return images