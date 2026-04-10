import os
import pygame
from view.renderer.SpriteLoader import SpriteLoader

BASE_PATH = os.getcwd()

class EnemyView:
    def __init__(self, enemy, enemy_type):
        print("📂 BASE_PATH:", BASE_PATH)
        print("📂 EXISTE BASE_PATH:", os.path.exists(BASE_PATH))
        print("📂 EXISTE ENEMIGOS:", os.path.exists(os.path.join(BASE_PATH, "assets")))
        self.enemy_type = enemy_type

        # 🔥 EXTRAER SOLO EL NÚMERO (Ej: "Troll 1" → "1")
        number = str(enemy_type).split(" ")[-1]

        # 🔥 RUTA REAL SEGÚN TU PROYECTO
        self.base_path = os.path.join(
            BASE_PATH, "assets", "images", "enemies", "trolls", number
        )

        print(f"📂 Cargando enemigo desde: {self.base_path}")

        # --- CARGA DE ANIMACIONES ---
        try:
            self.walk_frames = SpriteLoader.load_animation(
                os.path.join(self.base_path, "walk")
            )
            self.attack_frames = SpriteLoader.load_animation(
                os.path.join(self.base_path, "attack")
            )
        except Exception as e:
            print(f"❌ Error cargando animaciones: {e}")
            self.walk_frames = []
            self.attack_frames = []

        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = None

    def update(self, enemy):
        frames = self.attack_frames if enemy.state == "attacking" else self.walk_frames

        if frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(frames):
                self.frame_index = 0

            self.image = frames[int(self.frame_index)]
        else:
            self.image = None

    def draw(self, screen, enemy):
        if not self.image:
            pygame.draw.rect(screen, (255, 0, 0), (enemy.x - 20, enemy.y - 20, 40, 40))
        else:
            img = self.image
            if enemy.team == "B":
                img = pygame.transform.flip(img, True, False)

            img = pygame.transform.scale(img, (70, 70))
            rect = img.get_rect(center=(int(enemy.x), int(enemy.y)))
            screen.blit(img, rect)

        # --- LÓGICA DE LA BARRA DE VIDA ---
        self.draw_health_bar(screen, enemy)

    def draw_health_bar(self, screen, enemy):
        # Configuraciones de la barra
        BAR_WIDTH = 50
        BAR_HEIGHT = 6
        # Posicionarla un poco por encima de la cabeza del enemigo
        OFFSET_Y = 40 
        
        # Calcular el porcentaje de vida
        # Asumiendo que 'enemy' tiene los atributos 'hp' y 'max_hp'
        health_ratio = max(0, enemy.hp / enemy.max_hp)
        
        # Coordenadas de inicio (centrada respecto al enemigo)
        bar_x = enemy.x - (BAR_WIDTH / 2)
        bar_y = enemy.y - OFFSET_Y

        
        # 2. Barra de vida actual (Verde)
        # El ancho depende del porcentaje de vida
        current_health_width = BAR_WIDTH * health_ratio
        color = (0, 255, 0) if health_ratio > 0.3 else (255, 0, 0) # Cambia a rojo si es baja
        
        pygame.draw.rect(screen, color, (bar_x, bar_y, current_health_width, BAR_HEIGHT))
        
        # 3. Opcional: Un borde negro muy fino para que resalte
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT), 1)