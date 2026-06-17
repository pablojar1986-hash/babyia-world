"""
interface/mission_view.py — Panel de mision actual para BabyIA World 0.4.4.

Muestra objetivo, razon, distancias y progreso.
No contiene logica de entrenamiento.
"""

import pygame
from interface.ui_components import txt, bar, divider, ACCENT, TEXT_DIM
from interface.visual_theme import mission_color, distance_color

_GOAL_LABELS = {
    "FIND_KEY": "Buscar llave",
    "GO_TO_NEXT_LEVEL_DOOR": "Ir a puerta dorada (7,7)",
    "AVOID_DANGER": "Evitar peligro",
    "COLLECT_USEFUL_POWERUP": "Recoger powerup util",
    "RETURN_HOME": "Volver a casa",
    "LEVEL_COMPLETED": "Nivel completado!",
    "EXPLORE_OPTIONAL_ROOM": "Explorar sala opcional",
}

_DIST_LABELS = {
    "key_distance": "Dist. llave",
    "progress_door_distance": "Dist. puerta dorada",
}


def render(surface: pygame.Surface, fonts: dict, area: tuple, status: dict):
    x, y, w, _ = area
    py = y

    mission = status.get("mission", {})
    ctx = status.get("decision_context", {})
    mr = status.get("mission_reward", {})

    goal = mission.get("current_goal", "FIND_KEY")
    reason = mission.get("reason", "")
    progress = float(mission.get("progress_score", 0.0))
    target = mission.get("target_position")
    mc = mission_color(goal)

    # ── Titulo ────────────────────────────────────────────────────────────────
    txt(surface, "MISION ACTUAL", x, py, fonts["med"], ACCENT)
    py += 20

    label = _GOAL_LABELS.get(goal, goal)
    txt(surface, label[:30], x, py, fonts["med"], mc)
    py += 18

    if reason:
        txt(surface, reason[:40], x, py, fonts["xs"], TEXT_DIM)
        py += 14
    if target:
        txt(
            surface,
            f"Objetivo: ({target[0]},{target[1]})",
            x,
            py,
            fonts["xs"],
            TEXT_DIM,
        )
        py += 14

    # ── Barra de progreso de mision ───────────────────────────────────────────
    bar(
        surface,
        x,
        py,
        w - 4,
        "Progreso",
        progress,
        fonts["sm"],
        fonts["xs"],
        warn_at=None,
        label_w=80,
    )
    py += 22
    divider(surface, x, py, w - 4)
    py += 10

    # ── Estado del inventario ─────────────────────────────────────────────────
    txt(surface, "Estado de inventario", x, py, fonts["sm"], ACCENT)
    py += 18
    has_key = ctx.get("has_key", False)
    key_c = (80, 220, 80) if has_key else (180, 60, 60)
    txt(
        surface,
        f"Llave:         {'SI' if has_key else 'NO'}",
        x,
        py,
        fonts["sm"],
        key_c,
    )
    py += 16
    energy = ctx.get("energy", 1.0)
    energy_c = (80, 220, 80) if energy >= 0.4 else (220, 80, 80)
    txt(surface, f"Energia inv.:  {energy:.2f}", x, py, fonts["sm"], energy_c)
    py += 16

    prog_nearby = ctx.get("progress_door_nearby", False)
    prog_c = (255, 200, 0) if prog_nearby else TEXT_DIM
    txt(
        surface,
        f"Puerta cerca:  {'SI' if prog_nearby else 'no'}",
        x,
        py,
        fonts["xs"],
        prog_c,
    )
    py += 14
    divider(surface, x, py, w - 4)
    py += 10

    # ── Distancias ────────────────────────────────────────────────────────────
    txt(surface, "Distancias", x, py, fonts["sm"], ACCENT)
    py += 18
    for key, label in _DIST_LABELS.items():
        d = ctx.get(key, 1.0)
        dc = distance_color(d)
        txt(surface, f"{label[:18]}: {d:.2f}", x, py, fonts["xs"], dc)
        py += 14
    py += 4
    divider(surface, x, py, w - 4)
    py += 10

    # ── Reward shaping de mision ──────────────────────────────────────────────
    txt(surface, "Reward de mision (ep.)", x, py, fonts["sm"], ACCENT)
    py += 18
    mr_total = mr.get("total_mission_reward", 0.0)
    mr_c = (80, 220, 80) if mr_total >= 0 else (220, 80, 80)
    txt(surface, f"Total:      {mr_total:+.2f}", x, py, fonts["xs"], mr_c)
    py += 14
    txt(
        surface,
        f"Progreso:   {mr.get('progress_steps', 0)} pasos",
        x,
        py,
        fonts["xs"],
        TEXT_DIM,
    )
    py += 14
    txt(
        surface,
        f"Regresion:  {mr.get('regression_steps', 0)} pasos",
        x,
        py,
        fonts["xs"],
        TEXT_DIM,
    )
    py += 14
    txt(
        surface,
        f"Cambios:    {mr.get('mission_switches', 0)}",
        x,
        py,
        fonts["xs"],
        TEXT_DIM,
    )
    py += 14
    divider(surface, x, py, w - 4)
    py += 10

    # ── Estancamiento ─────────────────────────────────────────────────────────
    ewp = status.get("episodes_without_progress", 0)
    stag = status.get("stagnation_active", False)
    stag_c = (220, 70, 70) if stag else TEXT_DIM
    txt(surface, f"Sin progreso: {ewp} ep.", x, py, fonts["xs"], stag_c)
    py += 14
    lc = status.get("level_completions", 0)
    cur = status.get("curriculum", {})
    req = cur.get("required", 1)
    txt(surface, f"Completados:  {lc}/{req}", x, py, fonts["xs"], TEXT_DIM)
    py += 14

    return py
