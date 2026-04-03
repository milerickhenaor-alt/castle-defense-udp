import os
import pygame

class SpriteLoader:

    @staticmethod
    def load_animation(folder_path):
        frames = []
        for file in sorted(os.listdir(folder_path)):
            path = os.path.join(folder_path, file)
            img = pygame.image.load(path)
            frames.append(img)
        return frames