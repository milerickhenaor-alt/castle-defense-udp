from view.renderer.renderer import Renderer # Verifica que la capitalización coincida con tu archivo
from view.hud import Hud

class GameScreen:
    def __init__(self, screen, selections):
        self.screen = screen
        # 'selections' debe traer: {'players': [p1, p2, p3, p4], 'castle_a': '1', ...}
        self.renderer = Renderer(screen, selections)
        self.hud = Hud(screen)
        
    def update(self, game_state):
        """
        Aquí podrías manejar animaciones locales o efectos que 
        no dependen estrictamente del servidor.
        """
        pass

    def draw(self, game_state):
        if not game_state:
            return
            
        # 1. Dibujar el mundo (Fondo -> Castillos -> Enemigos -> Jugadores)
        self.renderer.render(game_state)
        
        # 2. Dibujar la capa superior (Interfaz, scores, tiempo)
        self.hud.draw(game_state)