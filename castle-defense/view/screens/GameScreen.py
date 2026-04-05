from view.renderer.renderer import Renderer 
from view.hud import Hud

class GameScreen:
    def __init__(self, screen, selections):
        self.screen = screen
        self.renderer = Renderer(screen, selections)
        self.hud = Hud(screen)

    def handle_event(self, event):
        pass

    def update(self, game_state):
        self.renderer.render(game_state)
        self.hud.draw(game_state)