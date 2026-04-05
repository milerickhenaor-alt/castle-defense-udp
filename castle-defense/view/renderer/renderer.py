from view.renderer.PlayerView import PlayerView

class Renderer:
    def __init__(self, screen, selections):
        self.screen = screen

        # 🔥 SOLO usa selección visual (NO GameState)
        self.player_views = [
            PlayerView(p) for p in selections["players"]
        ]

    def render(self, game_state):
        self.screen.fill((30, 30, 40))

        # 🔥 DIBUJAR JUGADORES SEGÚN MODEL
        for i, player in enumerate(game_state.players.values()):
            view = self.player_views[i]

            view.update()
            view.draw(self.screen, player.x, player.y)