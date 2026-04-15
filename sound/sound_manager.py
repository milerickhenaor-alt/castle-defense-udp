import pygame
import os

class SoundManager:
    def __init__(self, base_path):
        self.base_path = base_path
        pygame.mixer.init()
        
        # Diccionario para almacenar los sonidos
        self.sounds = {}
        
        # Cargar los sonidos (ajusta los nombres de archivo a tus assets)
        self._load_sound("shot", "shot.mp3")
        self._load_sound("troll_attack", "troll_attack.mp3")
        self._load_sound("castle_damage", "damage.mp3") # Opcional: cuando golpean el castillo
        
    def _load_sound(self, name, filename):
        """Carga un sonido de forma segura."""
        path = os.path.join(self.base_path, "assets", "sounds", filename)
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"❌ No se pudo cargar el sonido {filename}: {e}")
            # Creamos un objeto vacío para que el juego no se cierre si falta un sonido
            self.sounds[name] = None

    def play(self, name, volume=0.5):
        """Reproduce un sonido si existe."""
        sound = self.sounds.get(name)
        if sound:
            sound.set_volume(volume)
            sound.play()

# --- Ejemplo de integración ---
# En tu clase principal o GameState:
# self.audio = SoundManager(BASE_PATH)

# Cuando el jugador dispara:
# self.audio.play("shot")

# Cuando un troll ataca:
# self.audio.play("troll_attack")