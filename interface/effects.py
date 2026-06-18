"""
interface/effects.py — Efectos visuales simples para BabyIA 0.4.5.

Destellos y halos usando Pygame. Sin logica de entrenamiento.
"""

from __future__ import annotations

import pygame


def draw_key_flash(
    surface: pygame.Surface, cx: int, cy: int, radius: int, timer: float
):
    """Destello amarillo al recoger la llave. timer: 0.0 (nuevo) → 1.0 (desaparece)."""
    if timer <= 0:
        return
    r = int(radius * (1.0 + timer * 0.5))
    color = (255, 220, 60)
    pygame.draw.circle(surface, color, (cx, cy), r, max(1, int(3 * (1 - timer))))
    if timer < 0.6:
        r2 = int(radius * (1.3 + timer * 0.8))
        pygame.draw.circle(surface, (255, 240, 120), (cx, cy), r2, 1)


def draw_powerup_halo(
    surface: pygame.Surface, cx: int, cy: int, radius: int, timer: float
):
    """Halo de color al recoger un powerup. timer: 0.0 → 1.0."""
    if timer <= 0:
        return
    r = int(radius * (1.0 + timer * 0.8))
    pygame.draw.circle(surface, (60, 210, 240), (cx, cy), r, max(1, 2))
