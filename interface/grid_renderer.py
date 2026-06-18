"""
interface/grid_renderer.py — Dibuja el grid del mundo en pantalla.

BabyIA 0.4.6c: soporta vista completa escalada (full) y viewport (camera).
"""

from __future__ import annotations

import pygame
from interface.grid_scaler import (
    get_grid_draw_origin,
    get_scaled_cell_size,
    should_draw_compact_label,
    should_draw_label,
    world_to_fullmap_screen,
)
from world.objects import Cell

# ── Colores del grid ──────────────────────────────────────────────────────────
_EMPTY = (42, 44, 56)
_VISIT = (55, 80, 130)
_WALL = (90, 90, 100)
_GOAL = (50, 200, 90)
_KEY = (255, 220, 80)
_DOOR_C = (160, 80, 40)
_DOOR_O = (100, 160, 80)
_FOOD = (80, 200, 120)
_DANGER = (200, 60, 60)
_UNKNWN = (140, 80, 200)
_POWERUP = (60, 200, 240)
_HAZARD = (240, 110, 30)
_SPDOOR = (180, 90, 200)
_LVLDOOR = (255, 200, 0)
_OPTDOOR = (50, 220, 180)
_FOG = (20, 22, 30)

PORTAL_COLORS: dict[tuple[int, int], tuple[int, int, int]] = {
    (7, 2): (50, 130, 220),
    (7, 4): (210, 50, 50),
    (7, 6): (50, 200, 80),
    (6, 7): (255, 200, 0),
    (0, 0): (200, 200, 255),
}

CELL_COLORS: dict[int, tuple[int, int, int]] = {
    int(Cell.WALL): _WALL,
    int(Cell.GOAL): _GOAL,
    int(Cell.KEY): _KEY,
    int(Cell.DOOR_CLOSED): _DOOR_C,
    int(Cell.DOOR_OPEN): _DOOR_O,
    int(Cell.FOOD): _FOOD,
    int(Cell.DANGER): _DANGER,
    int(Cell.UNKNOWN_OBJECT): _UNKNWN,
    int(Cell.POWERUP): _POWERUP,
    int(Cell.HAZARD): _HAZARD,
    int(Cell.SPECIAL_DOOR): _SPDOOR,
    int(Cell.LEVEL_DOOR): _LVLDOOR,
    int(Cell.OPTIONAL_DOOR): _OPTDOOR,
}

CELL_LABELS: dict[Cell, tuple[str, tuple[int, int, int]]] = {
    Cell.GOAL: ("META", (10, 40, 20)),
    Cell.KEY: ("K", (80, 60, 10)),
    Cell.DOOR_CLOSED: ("D", (60, 30, 10)),
    Cell.DOOR_OPEN: ("O", (30, 60, 20)),
    Cell.FOOD: ("F", (20, 60, 30)),
    Cell.DANGER: ("X", (80, 20, 20)),
    Cell.UNKNOWN_OBJECT: ("?", (50, 20, 80)),
    Cell.POWERUP: ("+", (10, 70, 90)),
    Cell.HAZARD: ("!", (90, 30, 10)),
    Cell.SPECIAL_DOOR: ("S", (60, 20, 70)),
    Cell.LEVEL_DOOR: ("N", (80, 60, 0)),
    Cell.OPTIONAL_DOOR: ("O", (10, 70, 60)),
}

_VALID_CELL_VALUES: frozenset[int] = frozenset(c.value for c in Cell)


def _draw_cell(
    screen: pygame.Surface,
    sx: int,
    sy: int,
    cs: int,
    val: int,
    visited: set,
    wx: int,
    wy: int,
    fonts: dict,
    full_lbl: bool,
    compact_lbl: bool,
    fog: bool = False,
) -> None:
    rect = pygame.Rect(sx, sy, cs - 2, cs - 2)
    is_vis = (wx, wy) in visited

    if fog and not is_vis:
        pygame.draw.rect(screen, _FOG, rect, border_radius=4)
        return

    portal_c = PORTAL_COLORS.get((wx, wy))
    base_color = CELL_COLORS.get(val, _VISIT if is_vis else _EMPTY)
    pygame.draw.rect(screen, base_color, rect, border_radius=4)

    if portal_c:
        pygame.draw.rect(screen, portal_c, rect, width=3, border_radius=4)
        if full_lbl or compact_lbl:
            p = fonts["xs"].render("P", True, portal_c)
            screen.blit(p, (sx + cs // 2 - 4, sy + 3))

    if full_lbl or compact_lbl:
        cell_e = Cell(val) if val in _VALID_CELL_VALUES else None
        if cell_e and cell_e in CELL_LABELS:
            lbl_txt, lbl_clr = CELL_LABELS[cell_e]
            lbl = fonts["xs"].render(lbl_txt, True, lbl_clr)
            screen.blit(lbl, (sx + cs // 2 - 6, sy + cs // 2 - 6))


def draw_full_world(
    screen: pygame.Surface,
    world,
    status: dict,
    fonts: dict,
    avatar,
    grid_area: tuple,
    fog: bool = True,
) -> int:
    """Dibuja el mundo completo escalado. Devuelve el cell_size usado."""
    grid = world.get_grid()
    visited = world.visited
    world_size = getattr(world, "size", 8)
    bx, by = world.baby_pos

    cs = get_scaled_cell_size(grid_area, world_size)
    ox, oy = get_grid_draw_origin(grid_area, world_size, cs)
    full_lbl = should_draw_label(cs)
    compact_lbl = should_draw_compact_label(cs)

    for wy in range(world_size):
        for wx in range(world_size):
            sx, sy = world_to_fullmap_screen((wx, wy), (ox, oy), cs)
            _draw_cell(
                screen,
                sx,
                sy,
                cs,
                grid[wy][wx],
                visited,
                wx,
                wy,
                fonts,
                full_lbl,
                compact_lbl,
                fog,
            )

    av_sx, av_sy = world_to_fullmap_screen((bx, by), (ox, oy), cs)
    avatar.draw(
        screen,
        av_sx + cs // 2,
        av_sy + cs // 2,
        cs,
        status.get("level", 0),
        status.get("emotions", {}),
        status.get("body_state", {}),
        mission_goal=status.get("mission", {}).get("current_goal", ""),
    )
    return cs


def draw_camera_world(
    screen: pygame.Surface,
    world,
    status: dict,
    fonts: dict,
    avatar,
    camera,
    grid_area: tuple,
    cell_size: int,
) -> None:
    """Dibuja solo el viewport de la camara (modo clasico 8x8)."""
    grid = world.get_grid()
    visited = world.visited
    world_size = getattr(world, "size", 8)
    bx, by = world.baby_pos
    ox, oy = grid_area[0], grid_area[1]

    camera.update((bx, by), grid_size=world_size)
    mn_x, mn_y, mx_x, mx_y = camera.get_visible_bounds()

    for wy in range(mn_y, mx_y):
        for wx in range(mn_x, mx_x):
            sx, sy = camera.world_to_screen(wx, wy, cell_size, ox, oy)
            _draw_cell(
                screen,
                sx,
                sy,
                cell_size,
                grid[wy][wx],
                visited,
                wx,
                wy,
                fonts,
                True,
                False,
            )

    av_sx, av_sy = camera.world_to_screen(bx, by, cell_size, ox, oy)
    avatar.draw(
        screen,
        av_sx + cell_size // 2,
        av_sy + cell_size // 2,
        cell_size,
        status.get("level", 0),
        status.get("emotions", {}),
        status.get("body_state", {}),
        mission_goal=status.get("mission", {}).get("current_goal", ""),
    )


def draw_view_info(
    screen: pygame.Surface,
    fonts: dict,
    grid_area: tuple,
    view_mode: str,
    world_size: int,
    cell_size: int,
) -> None:
    """Overlay en esquina inferior del grid con modo y escala activos."""
    gx, gy, gw, gh = grid_area
    if view_mode == "full":
        text = f"FULL {world_size}x{world_size}@{cell_size}px  [C]:camara"
    else:
        text = f"CAM 8x8@{cell_size}px  [F]:completo"
    surf = fonts["xs"].render(text, True, (180, 180, 180))
    screen.blit(surf, (gx + 4, gy + gh - 16))
