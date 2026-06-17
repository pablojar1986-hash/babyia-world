"""
Renderizador del avatar de BabyIA para Pygame.
El avatar cambia visualmente segun nivel y senales internas.
Estas son representaciones graficas, no indicadores de conciencia real.
"""
import pygame

# Colores base por nivel (nivel 0-7+)
_LEVEL_COLORS = {
    0: (200, 160,  50),
    1: (220, 180,  60),
    2: (100, 180, 240),
    3: ( 80, 200, 120),
    4: (200, 120, 240),
    5: (240, 160,  80),
    6: (240, 240, 100),
    7: (255, 220,  50),
}
_DARK = (30, 30, 40)


class AvatarRenderer:
    """Dibuja a BabyIA en el grid con variaciones por nivel y senales internas."""

    def __init__(self):
        self._font_xs: pygame.font.Font | None = None

    def _init_fonts(self):
        if self._font_xs is None:
            self._font_xs = pygame.font.SysFont("consolas", 10)

    def draw(self, surface: pygame.Surface, cx: int, cy: int, cell_size: int,
             level: int, emotions: dict, body_state: dict | None = None):
        """
        Dibuja el avatar en la posicion central (cx, cy).
        emotions: dict con curiosity, confidence, frustration, energy.
        body_state (0.4): dict con size, speed, shield, fire_immunity, poison_immunity.
        """
        self._init_fonts()
        bs     = body_state or {}
        # 0.4: radio escala con tamano corporal (size 0.5-3.0 → factor 0.75-1.5)
        b_size = float(bs.get("size", 1.0))
        scale  = 0.75 + 0.25 * b_size
        r      = max(5, int((cell_size // 2 - 7) * scale))

        energy = float(emotions.get("energy", 1.0))
        conf   = float(emotions.get("confidence", 0.5))
        frust  = float(emotions.get("frustration", 0.0))
        curio  = float(emotions.get("curiosity", 0.5))

        base  = _LEVEL_COLORS.get(min(level, 7), (200, 200, 200))
        color = self._tint(base, energy, curio)

        # 0.4: escudo activo → halo azul exterior
        shield = float(bs.get("shield", 0.0))
        if shield > 0.05:
            s_r = r + int(shield * 5) + 2
            pygame.draw.circle(surface, (80, 140, 255), (cx, cy), s_r, 2)

        # Cuerpo
        pygame.draw.circle(surface, color, (cx, cy), r)
        # Borde segun confianza
        bw = max(1, int(conf * 3))
        bc = tuple(min(255, c + 40) for c in color)
        pygame.draw.circle(surface, bc, (cx, cy), r, bw)

        # 0.4: inmunidad fuego → pequeno triangulo naranja encima
        if bs.get("fire_immunity"):
            pygame.draw.polygon(surface, (255, 120, 30), [
                (cx, cy - r - 8), (cx - 4, cy - r - 2), (cx + 4, cy - r - 2)
            ])
        # 0.4: inmunidad veneno → punto verde a la derecha
        if bs.get("poison_immunity"):
            pygame.draw.circle(surface, (60, 220, 80), (cx + r + 4, cy - r + 2), 3)

        if level >= 1:
            # Ojos
            pygame.draw.circle(surface, _DARK, (cx - 4, cy - 3), 2)
            pygame.draw.circle(surface, _DARK, (cx + 4, cy - 3), 2)
            # Boca
            if frust > 0.6:
                pygame.draw.arc(surface, _DARK,
                                pygame.Rect(cx - 4, cy + 2, 8, 6), 0, 3.14, 1)
            else:
                pygame.draw.arc(surface, _DARK,
                                pygame.Rect(cx - 4, cy + 3, 8, 5), 3.14, 6.28, 1)

        if level >= 3:
            # Mochila simbolica (pequeno rectangulo)
            pygame.draw.rect(surface, (100, 80, 60),
                             pygame.Rect(cx + r - 4, cy - 3, 5, 6))

        if level >= 5 and energy > 0.8:
            # Aura de energia
            for ddx, ddy in [(-r - 3, 0), (r + 3, 0), (0, -r - 3)]:
                pygame.draw.circle(surface, (255, 240, 100),
                                   (cx + ddx, cy + ddy), 2)

        if level >= 7:
            # Estrella de explorador
            pygame.draw.circle(surface, (255, 220, 50), (cx, cy - r - 5), 3)

    @staticmethod
    def _tint(base: tuple, energy: float, curiosity: float) -> tuple:
        r, g, b = base
        factor  = 0.5 + 0.5 * max(0.0, min(1.0, energy))
        r = int(r * factor)
        g = int(g * factor)
        b = min(255, int(b * factor) + (30 if curiosity > 0.7 else 0))
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
