"""
interface/effects.py — Efectos visuales simples para BabyIA 0.4.5.

Destellos, halos y pulsos usando Pygame. Sin logica de entrenamiento.
"""

from __future__ import annotations

import math
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
    # Segunda onda
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


def draw_damage_border(surface: pygame.Surface, rect: pygame.Rect, timer: float):
    """Borde rojo al recibir daño. timer: 0.0 → 1.0."""
    if timer <= 0:
        return
    thickness = max(1, int(6 * (1.0 - timer)))
    alpha_factor = 1.0 - timer
    r = int(220 * alpha_factor)
    pygame.draw.rect(surface, (r, 40, 40), rect, thickness)


def draw_level_complete_pulse(
    surface: pygame.Surface, cx: int, cy: int, radius: int, timer: float
):
    """Pulso dorado al completar nivel. timer: 0.0 → 1.0 (ciclo)."""
    if timer <= 0:
        return
    pulse = abs(math.sin(timer * math.pi * 3))
    r = int(radius * (1.0 + pulse * 0.6))
    color = (255, 215, int(50 + 100 * pulse))
    pygame.draw.circle(surface, color, (cx, cy), r, max(2, int(4 * pulse)))


def draw_objective_marker(
    surface: pygame.Surface,
    cx: int,
    cy: int,
    cell_size: int,
    color: tuple = (255, 220, 60),
):
    """Pequena marca en la celda objetivo funcional actual."""
    s = max(3, cell_size // 8)
    pygame.draw.circle(surface, color, (cx, cy - cell_size // 3), s)
