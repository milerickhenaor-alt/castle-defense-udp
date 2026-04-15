"""
view/screens/GameOverScreen.py
Persona 1 — Pantalla final del juego

Muestra:
  - Título GAME OVER
  - Equipo ganador
  - Nombres y puntajes de todos los jugadores
  - Vida restante de cada castillo
  - Tiempo total de juego
"""

import pygame
from utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE, BLACK, GREEN, RED, YELLOW, GRAY,
    FONT_NAME, FONT_LARGE, FONT_MEDIUM, FONT_SMALL,
)


class GameOverScreen:
    """
    Pantalla final que se muestra cuando termina la partida.

    Recibe el game_state completo y extrae:
      - winner_team
      - jugadores de cada equipo con sus puntajes
      - vida restante de los castillos
      - tiempo total jugado
    """

    # Colores específicos de la pantalla
    COLOR_TEAM_A    = (100, 180, 255)   # Azul claro para equipo A
    COLOR_TEAM_B    = (255, 120, 120)   # Rojo claro para equipo B
    COLOR_WINNER    = (255, 215, 0)     # Dorado para el ganador
    COLOR_BG_TOP    = (10,  10,  30)    # Fondo degradado superior
    COLOR_SEPARATOR = (80,  80,  80)    # Línea separadora

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        pygame.font.init()

        self.font_title  = pygame.font.SysFont(FONT_NAME, FONT_LARGE + 20, bold=True)
        self.font_large  = pygame.font.SysFont(FONT_NAME, FONT_LARGE,  bold=True)
        self.font_medium = pygame.font.SysFont(FONT_NAME, FONT_MEDIUM)
        self.font_small  = pygame.font.SysFont(FONT_NAME, FONT_SMALL)
        self.btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 125, 500, 250, 45)
    # ------------------------------------------------------------------ #
    #  Eventos                                                             #
    # ------------------------------------------------------------------ #

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Retorna True si el jugador hizo clic en el botón de reinicio."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_rect.collidepoint(event.pos):
                return True
        return False

    # ------------------------------------------------------------------ #
    #  Dibujo principal                                                    #
    # ------------------------------------------------------------------ #

    def draw(self, game_state) -> None:
        """
        Dibuja la pantalla completa de fin de juego.

        Parameters
        ----------
        game_state : GameState con winner_team, players, castles y elapsed_time
        """
        self.screen.fill(BLACK)
        self._draw_background()

        # Extraer datos del GameState
        winner_team = game_state.winner_team
        players     = list(game_state.players.values())
        castles     = game_state.castles
        elapsed     = game_state.game_duration - game_state.remaining_time

        players_a = sorted(
            [p for p in players if p.team == "A"],
            key=lambda p: p.score, reverse=True
        )
        players_b = sorted(
            [p for p in players if p.team == "B"],
            key=lambda p: p.score, reverse=True
        )

        score_a = sum(p.score for p in players_a)
        score_b = sum(p.score for p in players_b)

        cx = SCREEN_WIDTH // 2

        # --- PAUSA VISUAL: Usamos el tiempo que quedó en el game_state ---
        elapsed = game_state.game_duration - game_state.remaining_time

        # ── Título ────────────────────────────────────────────────────── #
        self._draw_centered("GAME OVER", self.font_title, COLOR_USE=self.COLOR_WINNER, y=30)

        # ── Ganador ───────────────────────────────────────────────────── #
        if winner_team == "A":
            winner_text = "¡EQUIPO A GANA!"
            winner_color = self.COLOR_TEAM_A
        elif winner_team == "B":
            winner_text = "¡EQUIPO B GANA!"
            winner_color = self.COLOR_TEAM_B
        else:
            winner_text = "¡EMPATE!"
            winner_color = YELLOW

        self._draw_centered(winner_text, self.font_large, COLOR_USE=winner_color, y=100)

        # --- DIBUJAR BOTÓN DE REINICIO ---
        mouse_pos = pygame.mouse.get_pos()
        btn_color = self.COLOR_WINNER if self.btn_rect.collidepoint(mouse_pos) else self.COLOR_BTN
        
        pygame.draw.rect(self.screen, btn_color, self.btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.btn_rect, 2, border_radius=10)
        
        txt_btn = self.font_medium.render("VOLVER AL MENÚ", True, WHITE)
        self.screen.blit(txt_btn, (self.btn_rect.centerx - txt_btn.get_width()//2, 
                                    self.btn_rect.centery - txt_btn.get_height()//2))

        # Dibujar tiempo (estático porque elapsed ya no cambia)
        mins, secs = int(elapsed) // 60, int(elapsed) % 60
        self._draw_centered(f"Tiempo Final: {mins:02d}:{secs:02d}", self.font_small, GRAY, 460)

        # ── Línea separadora ──────────────────────────────────────────── #
        pygame.draw.line(self.screen, self.COLOR_SEPARATOR,
                         (50, 155), (SCREEN_WIDTH - 50, 155), 2)

        # ── Puntajes por equipo ───────────────────────────────────────── #
        self._draw_team_panel(
            title="EQUIPO A",
            players=players_a,
            total_score=score_a,
            castle=castles.get("A"),
            color=self.COLOR_TEAM_A,
            x_start=60,
            y_start=170,
            is_winner=(winner_team == "A"),
        )

        self._draw_team_panel(
            title="EQUIPO B",
            players=players_b,
            total_score=score_b,
            castle=castles.get("B"),
            color=self.COLOR_TEAM_B,
            x_start=cx + 30,
            y_start=170,
            is_winner=(winner_team == "B"),
        )

        # ── Línea vertical central ────────────────────────────────────── #
        pygame.draw.line(self.screen, self.COLOR_SEPARATOR,
                         (cx, 155), (cx, 430), 2)

        # ── Marcador global ───────────────────────────────────────────── #
        pygame.draw.line(self.screen, self.COLOR_SEPARATOR,
                         (50, 435), (SCREEN_WIDTH - 50, 435), 2)

        score_str = f"{score_a}  vs  {score_b}"
        self._draw_centered(score_str, self.font_large, COLOR_USE=WHITE, y=450)

        score_label = self._render(self.font_small, "Puntaje total  A   -   B", GRAY)
        self.screen.blit(score_label, (cx - score_label.get_width() // 2, 500))

        # ── Tiempo total ──────────────────────────────────────────────── #
        mins  = int(elapsed) // 60
        secs  = int(elapsed) % 60
        time_str = f"Tiempo de juego: {mins:02d}:{secs:02d}"
        self._draw_centered(time_str, self.font_small, COLOR_USE=GRAY, y=535)

        # ── Instrucción salir ─────────────────────────────────────────── #
        self._draw_centered("Cierra la ventana para salir",
                            self.font_small, COLOR_USE=GRAY, y=565)

    # ------------------------------------------------------------------ #
    #  Panel de equipo                                                     #
    # ------------------------------------------------------------------ #

    def _draw_team_panel(
        self,
        title: str,
        players: list,
        total_score: int,
        castle,
        color: tuple,
        x_start: int,
        y_start: int,
        is_winner: bool,
    ) -> None:
        """Dibuja el panel de un equipo con jugadores, puntajes y vida del castillo."""

        # Título del equipo
        label = self.font_medium.render(title, True, color)
        if is_winner:
            # Corona dorada al lado del ganador
            crown = self.font_medium.render("*** " + title + " ***", True, self.COLOR_WINNER)
            self.screen.blit(crown, (x_start, y_start))
        else:
            self.screen.blit(label, (x_start, y_start))

        y = y_start + 40

        # Jugadores
        for i, player in enumerate(players):
            # Nombre
            name_surf = self.font_small.render(player.name, True, WHITE)
            self.screen.blit(name_surf, (x_start + 10, y))

            # Puntaje
            score_surf = self.font_small.render(str(player.score), True, YELLOW)
            self.screen.blit(score_surf, (x_start + 310, y))

            y += 30

        # Vida del castillo
        if castle:
            y += 10
            hp_text = f"Castillo: {castle.hp} / {castle.max_hp} HP"
            hp_color = GREEN if castle.hp_ratio > 0.5 else (YELLOW if castle.hp_ratio > 0.2 else RED)
            hp_surf = self.font_small.render(hp_text, True, hp_color)
            self.screen.blit(hp_surf, (x_start + 10, y))

            # Barra de vida del castillo
            y += 25
            bar_w = 360
            bar_h = 12
            pygame.draw.rect(self.screen, GRAY,
                             (x_start + 10, y, bar_w, bar_h))
            fill_w = int(bar_w * castle.hp_ratio)
            pygame.draw.rect(self.screen, hp_color,
                             (x_start + 10, y, fill_w, bar_h))

        # Puntaje total del equipo
        y += 30
        total_surf = self.font_medium.render(f"Total: {total_score} pts", True, color)
        self.screen.blit(total_surf, (x_start + 10, y))

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _draw_background(self) -> None:
        """Dibuja un fondo con gradiente sutil."""
        for i in range(SCREEN_HEIGHT):
            ratio = i / SCREEN_HEIGHT
            r = int(self.COLOR_BG_TOP[0] + (20 - self.COLOR_BG_TOP[0]) * ratio)
            g = int(self.COLOR_BG_TOP[1] + (10 - self.COLOR_BG_TOP[1]) * ratio)
            b = int(self.COLOR_BG_TOP[2] + (40 - self.COLOR_BG_TOP[2]) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))

    def _render(self, font, text: str, color: tuple) -> pygame.Surface:
        return font.render(text, True, color)

    def _draw_centered(self, text: str, font, COLOR_USE: tuple, y: int) -> None:
        surf = font.render(text, True, COLOR_USE)
        x = SCREEN_WIDTH // 2 - surf.get_width() // 2
        self.screen.blit(surf, (x, y))