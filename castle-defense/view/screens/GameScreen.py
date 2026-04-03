from view.renderer.Renderer import Renderer
from view.Hud import Hud

class GameScreen:
    def __init__(self, screen, selections):
        self.screen = screen
        self.renderer = Renderer(screen, selections)
        self.hud = Hud()

    def update(self, game_state):
        self.renderer.render(game_state)
        self.hud.draw(self.screen, game_state)