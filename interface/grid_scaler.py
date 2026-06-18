"""
interface/grid_scaler.py — Calculo de escala para vista completa del mundo.

Funciones puras sin dependencia de pygame — importables en tests.
Utilizadas por grid_renderer.py para la vista completa escalada.
"""

from __future__ import annotations


def get_scaled_cell_size(
    grid_area: tuple, world_size: int, min_cell_size: int = 16
) -> int:
    """
    Devuelve el tamano de celda maximo que permite mostrar world_size celdas
    dentro de grid_area sin scroll. Siempre >= min_cell_size.
    """
    _, _, gw, gh = grid_area
    cs = min(gw // world_size, gh // world_size)
    return max(min_cell_size, cs)


def get_grid_draw_origin(
    grid_area: tuple, world_size: int, cell_size: int
) -> tuple[int, int]:
    """
    Devuelve el pixel (ox, oy) del grid dentro de grid_area, centrado.
    Si el grid es mas pequeno que el area, hay margen a los lados.
    """
    gx, gy, gw, gh = grid_area
    total_w = world_size * cell_size
    total_h = world_size * cell_size
    ox = gx + (gw - total_w) // 2
    oy = gy + (gh - total_h) // 2
    return ox, oy


def world_to_fullmap_screen(
    pos: tuple, origin: tuple, cell_size: int
) -> tuple[int, int]:
    """
    Convierte coordenadas de mundo (wx, wy) a pixel de pantalla (sx, sy),
    que es la esquina superior-izquierda de la celda en vista completa.
    """
    wx, wy = pos
    ox, oy = origin
    return ox + wx * cell_size, oy + wy * cell_size


def is_in_grid_bounds(
    pos: tuple, origin: tuple, world_size: int, cell_size: int
) -> bool:
    """True si el pixel (sx, sy) cae dentro del rectangulo del mapa."""
    sx, sy = pos
    ox, oy = origin
    total = world_size * cell_size
    return ox <= sx < ox + total and oy <= sy < oy + total


def should_draw_label(cell_size: int) -> bool:
    """True si la celda es suficientemente grande para etiquetas completas."""
    return cell_size >= 40


def should_draw_compact_label(cell_size: int) -> bool:
    """True si la celda admite simbolos cortos (K, N, +, !, S)."""
    return 28 <= cell_size < 40
