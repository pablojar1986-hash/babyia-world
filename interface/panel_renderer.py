"""
Gestor de pestañas y enrutamiento de paneles para BabyIA World 0.4.1.
Maneja la navegación 1-5 / TAB / flechas y delega a los módulos de vista.
"""

import pygame
from interface.layout import TABS, TAB_COUNT, TAB_AREA, PANEL_AREA, PANEL_CONTENT
from interface.ui_components import (
    PANEL_BG,
    TAB_ACTIVE,
    TAB_INACT,
    TAB_ON,
    TAB_OFF,
    box,
)
import interface.status_view as _sv
import interface.world_info_view as _wv
import interface.body_view as _bv
import interface.brain_view as _brv
import interface.memory_view as _mv

_VIEWS = [_sv.render, _wv.render, _bv.render, _brv.render, _mv.render]


class PanelRenderer:
    """Renderiza el panel lateral con pestañas y maneja la navegación."""

    def __init__(self):
        self.active_tab: int = 0
        self._scroll: int = 0
        self._fonts: dict | None = None

    def set_fonts(self, fonts: dict):
        self._fonts = fonts

    # ── Navegación ────────────────────────────────────────────────────────────

    def handle_key(self, key: int, mods: int = 0) -> bool:
        """Devuelve True si la tecla fue consumida por el panel."""
        direct = {
            pygame.K_1: 0,
            pygame.K_2: 1,
            pygame.K_3: 2,
            pygame.K_4: 3,
            pygame.K_5: 4,
        }
        if key in direct:
            self._switch(direct[key])
            return True
        if key == pygame.K_TAB:
            shift = bool(mods & pygame.KMOD_SHIFT)
            self._switch((self.active_tab + (-1 if shift else 1)) % TAB_COUNT)
            return True
        if key in (pygame.K_UP, pygame.K_PAGEUP):
            step = 5 if key == pygame.K_PAGEUP else 1
            self._scroll = max(0, self._scroll - step)
            return True
        if key in (pygame.K_DOWN, pygame.K_PAGEDOWN):
            step = 5 if key == pygame.K_PAGEDOWN else 1
            self._scroll = min(60, self._scroll + step)
            return True
        return False

    # ── Dibujo ────────────────────────────────────────────────────────────────

    def render(self, surface: pygame.Surface, status: dict):
        if not self._fonts:
            return
        self._draw_tabs(surface)
        self._draw_content(surface, status)

    # ── Internos ──────────────────────────────────────────────────────────────

    def _switch(self, idx: int):
        self.active_tab = idx
        self._scroll = 0

    def _draw_tabs(self, surface: pygame.Surface):
        tx0, ty, tw, th = TAB_AREA
        pygame.draw.rect(surface, (10, 12, 20), (tx0, ty, tw, th))
        tab_w = tw // TAB_COUNT
        for i, name in enumerate(TABS):
            tx = tx0 + i * tab_w
            active = i == self.active_tab
            rect = pygame.Rect(tx + 1, ty + 3, tab_w - 2, th - 5)
            box(surface, rect, TAB_ACTIVE if active else TAB_INACT, radius=4)
            label = f"{i + 1} {name}"
            surf_l = self._fonts["xs"].render(
                label, True, TAB_ON if active else TAB_OFF
            )
            lw = surf_l.get_width()
            surface.blit(surf_l, (tx + (tab_w - lw) // 2, ty + 5))

    def _draw_content(self, surface: pygame.Surface, status: dict):
        px, py, pw, ph = PANEL_AREA
        # Fondo del panel
        pygame.draw.rect(surface, PANEL_BG, (px - 3, py, pw + 3, ph), border_radius=6)
        # Clip area bajo las pestañas
        cx, cy, cw, ch = PANEL_CONTENT
        clip = pygame.Rect(cx, cy, cw, ch)
        surface.set_clip(clip)

        # Scroll vertical: cada unidad = 16px
        scroll_offset = self._scroll * 16
        draw_area = (cx, cy - scroll_offset, cw, ch + scroll_offset + 200)

        _VIEWS[self.active_tab](surface, self._fonts, draw_area, status)

        surface.set_clip(None)
