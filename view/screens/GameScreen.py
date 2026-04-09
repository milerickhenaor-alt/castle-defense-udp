from view.renderer.renderer import Renderer
from view.hud import Hud


class GameScreen:
    def __init__(self, screen, selections):
        self.screen = screen
        # 'selections' ahora contiene la clave 'players'
        self.renderer = Renderer(screen, selections)
        self.hud = Hud(screen)
        
    def update(self, game_state):
        pass

    def draw(self, game_state):
        self.renderer.render(game_state)
        self.hud.draw(game_state)