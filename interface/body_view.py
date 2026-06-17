"""Panel Cuerpo: BodyState, energia, supervivencia funcional y utilidad."""

from interface.ui_components import (
    txt,
    bar,
    divider,
    ACCENT,
    TEXT,
    TEXT_DIM,
    COLOR_POS,
    COLOR_NEG,
)


def render(surface, fonts, area, status):
    x, y, w, _ = area
    py = y

    bs = status.get("body_state", {})
    txt(surface, "Estado Corporal", x, py, fonts["med"], ACCENT)
    py += 20

    size = bs.get("size", 1.0)
    speed = bs.get("speed", 1.0)
    shield = bs.get("shield", 0.0)
    f_imm = bs.get("fire_immunity", False)
    p_imm = bs.get("poison_immunity", False)
    vr = bs.get("vision_range", 3)
    mf = bs.get("memory_focus", 1.0)
    fx = bs.get("active_effects", 0)

    bar(
        surface,
        x,
        py,
        w - 4,
        "Tamano",
        size / 3.0,
        fonts["sm"],
        fonts["xs"],
        label_w=90,
    )
    py += 22
    bar(
        surface,
        x,
        py,
        w - 4,
        "Velocidad",
        speed / 3.0,
        fonts["sm"],
        fonts["xs"],
        label_w=90,
    )
    py += 22
    bar(
        surface,
        x,
        py,
        w - 4,
        "Escudo",
        shield,
        fonts["sm"],
        fonts["xs"],
        warn_at=0.15,
        label_w=90,
    )
    py += 22

    fi_c = (255, 130, 40) if f_imm else TEXT_DIM
    pi_c = (80, 220, 100) if p_imm else TEXT_DIM
    txt(
        surface,
        f"Fuego:  {'INMUNE' if f_imm else 'vulnerable'}",
        x,
        py,
        fonts["xs"],
        fi_c,
    )
    py += 14
    txt(
        surface,
        f"Veneno: {'INMUNE' if p_imm else 'vulnerable'}",
        x,
        py,
        fonts["xs"],
        pi_c,
    )
    py += 14
    txt(
        surface,
        f"Vision: {vr} celdas    Foco mem: {mf:.2f}",
        x,
        py,
        fonts["xs"],
        TEXT_DIM,
    )
    py += 14
    txt(surface, f"Efectos activos: {fx}", x, py, fonts["xs"], TEXT_DIM)
    py += 14

    # Energia del inventario (0.4.2)
    energy = status.get("inventory", {}).get("energy", 1.0)
    e_warn = 0.3
    bar(
        surface,
        x,
        py,
        w - 4,
        "Energia",
        energy,
        fonts["sm"],
        fonts["xs"],
        warn_at=e_warn,
        label_w=90,
    )
    py += 22
    py += 6
    divider(surface, x, py, w - 4)
    py += 10

    # Supervivencia funcional (0.4.2)
    sv = status.get("survival", {})
    if sv:
        txt(surface, "Supervivencia funcional", x, py, fonts["med"], ACCENT)
        py += 20
        rl = sv.get("risk_level", 0.0)
        rl_c = (
            (220, 70, 70) if rl > 0.6 else ((255, 165, 50) if rl > 0.3 else COLOR_POS)
        )
        txt(surface, f"Riesgo:    {rl:.2f}", x, py, fonts["sm"], rl_c)
        py += 16
        rec = sv.get("recommendation", "continuar")
        txt(surface, f"Accion:    {rec}", x, py, fonts["xs"], TEXT_DIM)
        py += 14
        nf = sv.get("needs_food", False)
        dp = sv.get("danger_without_protection", False)
        if nf:
            txt(
                surface,
                "  [!] Energia baja — buscar comida",
                x,
                py,
                fonts["xs"],
                (255, 165, 50),
            )
            py += 14
        if dp:
            txt(
                surface,
                "  [!] Peligro sin proteccion",
                x,
                py,
                fonts["xs"],
                (220, 70, 70),
            )
            py += 14
        py += 4
        divider(surface, x, py, w - 4)
        py += 10

    # Ultimo powerup / hazard / puerta (0.4.2)
    ev = status.get("ep_events", {})
    pu = ev.get("last_powerup")
    hz = ev.get("last_hazard")
    df = ev.get("last_door_fail")
    if pu or hz or df:
        txt(surface, "Ultimo evento corporal", x, py, fonts["med"], ACCENT)
        py += 20
        if pu:
            txt(surface, f"  Powerup: {pu}", x, py, fonts["xs"], (60, 200, 240))
            py += 14
        if hz:
            blk = ev.get("last_hazard_blocked", False)
            lbl = f"  Hazard: {hz} ({'bloqueado' if blk else 'afectado'})"
            txt(surface, lbl, x, py, fonts["xs"], TEXT if blk else (240, 110, 30))
            py += 14
        if df:
            txt(surface, f"  Puerta: {df}", x, py, fonts["xs"], (220, 70, 70))
            py += 14
        py += 4
        divider(surface, x, py, w - 4)
        py += 10

    util = status.get("utility", {})
    txt(surface, "Evaluador de Utilidad", x, py, fonts["med"], ACCENT)
    py += 20
    u = util.get("last_utility", 0.0)
    u_c = COLOR_POS if u >= 0 else COLOR_NEG
    txt(surface, f"Utilidad paso:   {u:+.4f}", x, py, fonts["sm"], u_c)
    py += 16
    avg_u = util.get("avg_episode_utility", 0.0)
    txt(surface, f"Prom episodio:   {avg_u:+.4f}", x, py, fonts["xs"], TEXT_DIM)
    py += 14
    txt(
        surface,
        f"Pasos evaluados: {util.get('steps_evaluated', 0)}",
        x,
        py,
        fonts["xs"],
        TEXT_DIM,
    )
    py += 14

    bd = util.get("last_breakdown", {})
    if bd:
        py += 6
        divider(surface, x, py, w - 4)
        py += 8
        txt(surface, "Desglose:", x, py, fonts["xs"], TEXT_DIM)
        py += 14
        for k, v in bd.items():
            if k != "total" and isinstance(v, (int, float)):
                sign = "+" if v >= 0 else ""
                txt(surface, f"  {k[:20]}: {sign}{v:.3f}", x, py, fonts["xs"], TEXT_DIM)
                py += 13
    return py
