import os
import pygame

class SpriteLoader:

    @staticmethod
    def load_animation(folder_path):
        frames = []

        if not os.path.exists(folder_path):
            print("❌ Carpeta no existe:", folder_path)
            return frames

        for file in sorted(os.listdir(folder_path)):
            if file.endswith(".png"):
                path = os.path.join(folder_path, file)
                try:
                    img = pygame.image.load(path).convert_alpha()
                    frames.append(img)
                except:
                    print("❌ Error cargando:", path)

        return frames