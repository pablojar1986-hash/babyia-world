"""
Componentes visuales reutilizables para BabyIA World 0.4.1.
Funciones puras de dibujo sin estado propio.
Importar colores desde aquí para coherencia visual entre paneles.
"""

import pygame

# ── Paleta global ─────────────────────────────────────────────────────────────
BG = (22, 24, 33)
PANEL_BG = (16, 18, 26)
TEXT = (220, 220, 230)
TEXT_DIM = (110, 115, 135)
ACCENT = (90, 170, 255)
BAR_BG = (35, 38, 52)
BAR_OK = (90, 170, 255)
BAR_WARN = (255, 165, 50)
BAR_DANGER = (220, 70, 70)
COLOR_POS = (100, 220, 100)
COLOR_NEG = (220, 90, 90)
DIVIDER_CLR = (40, 44, 60)
TAB_ACTIVE = (55, 80, 140)
TAB_INACT = (24, 26, 38)
TAB_ON = (210, 220, 255)
TAB_OFF = (80, 88, 120)
LOG_BG = (12, 14, 22)


# ── Primitivas ────────────────────────────────────────────────────────────────


def txt(
    surface: pygame.Surface,
    text: str,
    x: int,
    y: int,
    font: pygame.font.Font,
    color: tuple = TEXT,
):
    surface.blit(font.render(str(text), True, color), (x, y))


def divider(
    surface: pygame.Surface, x: int, y: int, width: int, color: tuple = DIVIDER_CLR
):
    pygame.draw.line(surface, color, (x, y), (x + width, y))


def box(
    surface: pygame.Surface,
    rect,
    fill: tuple,
    border: tuple | None = None,
    radius: int = 5,
):
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border, rect, width=1, border_radius=radius)


def bar(
    surface: pygame.Surface,
    x: int,
    y: int,
    width: int,
    label: str,
    value: float,
    font_sm: pygame.font.Font,
    font_xs: pygame.font.Font,
    warn_at: float | None = None,
    height: int = 12,
    label_w: int = 110,
):
    """Barra de progreso horizontal con etiqueta."""
    surface.blit(font_sm.render(f"{label}:", True, TEXT_DIM), (x, y))
    bx = x + label_w
    bw = max(10, width - label_w - 46)
    v = max(0.0, min(1.0, value))
    pygame.draw.rect(surface, BAR_BG, (bx, y + 2, bw, height), border_radius=4)
    fill_w = max(1, int(bw * v))
    if warn_at and value <= warn_at:
        clr = BAR_DANGER if value <= warn_at * 0.5 else BAR_WARN
    else:
        clr = BAR_OK
    pygame.draw.rect(surface, clr, (bx, y + 2, fill_w, height), border_radius=4)
    surface.blit(font_xs.render(f"{value:.2f}", True, TEXT), (bx + bw + 4, y + 1))


def h_bar(
    surface: pygame.Surface,
    x: int,
    y: int,
    width: int,
    value: float,
    min_v: float,
    max_v: float,
    color: tuple = BAR_OK,
    height: int = 10,
    font_xs: pygame.font.Font | None = None,
):
    """Barra horizontal con rango personalizado (para Q-values)."""
    span = max_v - min_v
    ratio = (value - min_v) / span if span > 1e-6 else 0.5
    ratio = max(0.0, min(1.0, ratio))
    pygame.draw.rect(surface, BAR_BG, (x, y, width, height), border_radius=3)
    fill_w = max(1, int(width * ratio))
    pygame.draw.rect(surface, color, (x, y, fill_w, height), border_radius=3)
    if font_xs:
        lbl = f"{value:+.3f}"
        surface.blit(font_xs.render(lbl, True, TEXT), (x + width + 4, y))
