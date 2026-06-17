"""
interface/minimap_view.py — Brujula textual de navegacion para BabyIA 0.4.4.

Muestra direcciones hacia objetivos clave (llave, puerta de progreso, peligros).
No contiene logica de entrenamiento.
"""

import pygame
from interface.ui_components import txt, divider, ACCENT, TEXT_DIM
from interface.visual_theme import mission_color, distance_color

_COMPASS_CHARS = {
    (-1, -1): "↖",
    (-1, 0): "←",
    (-1, 1): "↙",
    (0, -1): "↑",
    (0, 1): "↓",
    (1, -1): "↗",
    (1, 0): "→",
    (1, 1): "↘",
    (0, 0): "•",
}


def _direction(from_pos: tuple, to_pos: tuple) -> str:
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    if dx == 0 and dy == 0:
        return "•"
    sx = 0 if dx == 0 else (1 if dx > 0 else -1)
    sy = 0 if dy == 0 else (1 if dy > 0 else -1)
    return _COMPASS_CHARS.get((sx, sy), "?")


def _manhattan(a: tuple, b: tuple) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _render_target(
    surface,
    fonts,
    x: int,
    y: int,
    label: str,
    arrow: str,
    dist: int,
    color: tuple,
) -> int:
    txt(surface, label[:16], x, y, fonts["xs"], TEXT_DIM)
    txt(surface, f"  {arrow}  {dist} pasos", x + 8, y + 12, fonts["med"], color)
    return y + 30


def render(surface: pygame.Surface, fonts: dict, area: tuple, status: dict):
    x, y, w, _ = area
    py = y

    ctx = status.get("decision_context", {})
    mission = status.get("mission", {})
    baby_info = status.get("baby", {})

    # Posicion actual de BabyIA
    bpos_raw = baby_info.get("position", None)
    bpos = tuple(bpos_raw) if bpos_raw else (0, 0)
    goal = mission.get("current_goal", "FIND_KEY")

    txt(surface, "BRUJULA DE NAVEGACION", x, py, fonts["med"], ACCENT)
    py += 20
    txt(surface, f"Pos: ({bpos[0]},{bpos[1]})", x, py, fonts["xs"], TEXT_DIM)
    py += 16
    divider(surface, x, py, w - 4)
    py += 10

    # ── Llave ─────────────────────────────────────────────────────────────────
    KEY_POS = (1, 6)
    has_key = ctx.get("has_key", False)
    if not has_key:
        arrow = _direction(bpos, KEY_POS)
        dist = _manhattan(bpos, KEY_POS)
        dn = min(1.0, dist / 10.0)
        py = _render_target(
            surface, fonts, x, py, "Llave (1,6)", arrow, dist, distance_color(dn)
        )
    else:
        txt(surface, "Llave: OBTENIDA ✓", x, py, fonts["sm"], (80, 220, 80))
        py += 18

    divider(surface, x, py, w - 4)
    py += 10

    # ── Puerta de progreso (7,7) ──────────────────────────────────────────────
    PROG_DOOR_POS = (7, 7)
    arrow = _direction(bpos, PROG_DOOR_POS)
    dist = _manhattan(bpos, PROG_DOOR_POS)
    dn = min(1.0, dist / 10.0)
    mc = mission_color("GO_TO_NEXT_LEVEL_DOOR")
    py = _render_target(surface, fonts, x, py, "Puerta dorada (7,7)", arrow, dist, mc)

    divider(surface, x, py, w - 4)
    py += 10

    # ── Objetivo de mision actual ─────────────────────────────────────────────
    target = mission.get("target_position")
    if target and tuple(target) not in (KEY_POS, PROG_DOOR_POS):
        tpos = tuple(target)
        arrow = _direction(bpos, tpos)
        dist = _manhattan(bpos, tpos)
        dn = min(1.0, dist / 10.0)
        py = _render_target(
            surface,
            fonts,
            x,
            py,
            f"Obj. mision ({tpos[0]},{tpos[1]})",
            arrow,
            dist,
            mission_color(goal),
        )
        divider(surface, x, py, w - 4)
        py += 10

    # ── Amenaza mas cercana ────────────────────────────────────────────────────
    threat = ctx.get("nearest_threat")
    if threat:
        # nearest_threat es un id de hazard (str), no posicion — solo mostrar aviso
        danger_c = (220, 70, 70)
        txt(
            surface,
            f"! PELIGRO CERCANO: {str(threat)[:12]}",
            x,
            py,
            fonts["sm"],
            danger_c,
        )
        py += 18
        divider(surface, x, py, w - 4)
        py += 10

    # ── Powerup util ──────────────────────────────────────────────────────────
    powerup = ctx.get("nearest_useful_powerup")
    if powerup:
        pu_c = (60, 210, 240)
        txt(surface, f"~ Powerup util: {str(powerup)[:14]}", x, py, fonts["xs"], pu_c)
        py += 14

    txt(surface, f"Mision: {goal}", x, py, fonts["xs"], TEXT_DIM)
    py += 14

    return py
