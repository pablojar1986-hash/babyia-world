"""
interface/perception_view.py — Panel de percepcion funcional para BabyIA 0.4.5.

Muestra lo que BabyIA detecta en su rango de vision:
objetos cercanos, categorias semanticas, memoria visual del episodio.
"Ver" = detectar; no implica conciencia.
"""

from __future__ import annotations

import pygame
from interface.ui_components import txt, divider, ACCENT

# Colores locales (ui_components no los exporta)
_WHITE = (220, 220, 230)
_GREEN = (100, 220, 100)
_RED = (220, 90, 90)
_YELLOW = (255, 220, 60)
_CYAN = (60, 210, 240)
_GRAY = (100, 105, 130)
_ORANGE = (255, 165, 50)


def _hdr(surface, font, label, x, y):
    divider(surface, x, y, 200)
    txt(surface, label, x, y - 1, font, ACCENT)


def render(surface: pygame.Surface, fonts: dict, area: tuple, status: dict):
    x, y, w, h = area
    f_sm = fonts.get("sm")
    f_xs = fonts.get("xs")
    if not f_sm or not f_xs:
        return

    perception = status.get("perception", {})
    semantic = status.get("semantic_view", [])
    visual_mem = status.get("visual_memory", {})

    cy = y

    # ── Encabezado ────────────────────────────────────────────────────────────
    txt(surface, "PERCEPCION VISUAL", x, cy, f_sm, ACCENT)
    cy += 18

    if not perception:
        txt(surface, "Sin datos de percepcion", x, cy, f_xs, _GRAY)
        return

    # ── Rango de vision ───────────────────────────────────────────────────────
    vision_range = perception.get("vision_range", 0)
    total_visible = perception.get("total_visible", 0)
    danger_count = perception.get("danger_count", 0)
    reward_count = perception.get("reward_count", 0)

    txt(
        surface,
        f"Rango: {vision_range}  Detectados: {total_visible}",
        x,
        cy,
        f_xs,
        _WHITE,
    )
    cy += 14
    peligro_color = _RED if danger_count > 0 else _GRAY
    txt(
        surface,
        f"Peligros: {danger_count}  Recompensas: {reward_count}",
        x,
        cy,
        f_xs,
        peligro_color,
    )
    cy += 18

    # ── Objetos mas cercanos ──────────────────────────────────────────────────
    txt(surface, "MAS CERCANOS", x, cy, f_sm, ACCENT)
    cy += 16

    nearby = [
        ("Llave", "nearest_key", _YELLOW),
        ("Puerta prog.", "nearest_progress_door", _GREEN),
        ("Powerup", "nearest_powerup", _CYAN),
        ("Hazard", "nearest_hazard", _RED),
        ("Comida", "nearest_food", _ORANGE),
    ]

    for label, key, color in nearby:
        obj = perception.get(key)
        if obj:
            pos = obj.get("position", [0, 0])
            dist = obj.get("distance", 0)
            txt(surface, f"{label}: ({pos[0]},{pos[1]}) d={dist}", x, cy, f_xs, color)
        else:
            txt(surface, f"{label}: no visible", x, cy, f_xs, _GRAY)
        cy += 13

    cy += 5

    # ── Vista semantica (hasta 6 objetos) ─────────────────────────────────────
    if semantic:
        txt(surface, "CLASIFICACION SEMANTICA", x, cy, f_sm, ACCENT)
        cy += 16

        shown = 0
        for sem in sorted(semantic, key=lambda o: o.get("distance", 99)):
            if shown >= 6:
                break
            cat = sem.get("category", "?")
            util = sem.get("utility", 0.0)
            risk = sem.get("risk", 0.0)
            meaning = sem.get("meaning", "")[:24]

            color = _WHITE
            if cat == "DANGER":
                color = _RED
            elif cat == "GOAL_RELATED":
                color = _YELLOW
            elif cat == "REWARD":
                color = _GREEN
            elif cat == "OPTIONAL":
                color = _CYAN

            txt(
                surface,
                f"{meaning[:18]} U:{util:+.1f} R:{risk:.1f}",
                x,
                cy,
                f_xs,
                color,
            )
            cy += 13
            shown += 1

        cy += 5

    # ── Memoria visual del episodio ───────────────────────────────────────────
    if visual_mem:
        txt(surface, "MEMORIA VISUAL (EPISODIO)", x, cy, f_sm, ACCENT)
        cy += 16

        seen_pos = visual_mem.get("seen_positions_count", 0)
        safe = visual_mem.get("known_safe_count", 0)
        danger = visual_mem.get("known_danger_count", 0)
        times_key = visual_mem.get("times_key_seen", 0)
        times_door = visual_mem.get("times_progress_door_seen", 0)
        last_key = visual_mem.get("last_seen_key")
        last_door = visual_mem.get("last_seen_progress_door")
        last_hz = visual_mem.get("last_seen_hazards_count", 0)

        txt(surface, f"Celdas exploradas: {seen_pos}", x, cy, f_xs, _WHITE)
        cy += 13
        txt(surface, f"Seguras / Peligrosas: {safe} / {danger}", x, cy, f_xs, _WHITE)
        cy += 13

        if last_key:
            txt(
                surface,
                f"Llave: ({last_key[0]},{last_key[1]}) x{times_key}",
                x,
                cy,
                f_xs,
                _YELLOW,
            )
        else:
            txt(surface, "Llave: no vista aun", x, cy, f_xs, _GRAY)
        cy += 13

        if last_door:
            txt(
                surface,
                f"Puerta: ({last_door[0]},{last_door[1]}) x{times_door}",
                x,
                cy,
                f_xs,
                _GREEN,
            )
        else:
            txt(surface, "Puerta progreso: no vista", x, cy, f_xs, _GRAY)
        cy += 13

        hz_color = _RED if last_hz > 0 else _GRAY
        txt(surface, f"Hazards registrados: {last_hz}", x, cy, f_xs, hz_color)
