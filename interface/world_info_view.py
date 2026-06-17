"""Panel Mundo: mundo actual, portales, retorno a casa y preferencias."""

from interface.ui_components import (
    txt,
    bar,
    divider,
    ACCENT,
    TEXT_DIM,
)


def render(surface, fonts, area, status):
    x, y, w, _ = area
    py = y

    wi = status.get("world_info", {})
    wname = wi.get("world_id", "home").replace("_", " ")
    home_c = (100, 220, 100) if wi.get("is_at_home", True) else (255, 180, 50)

    txt(surface, "Mundo Actual", x, py, fonts["med"], ACCENT)
    py += 20
    txt(surface, f"ID:          {wname[:20]}", x, py, fonts["sm"], home_c)
    py += 16
    at_home = "SI" if wi.get("is_at_home", True) else "NO"
    txt(surface, f"En casa:     {at_home}", x, py, fonts["xs"], home_c)
    py += 14
    portal = wi.get("last_portal") or "-"
    txt(surface, f"Portal:      {portal[:18]}", x, py, fonts["xs"], TEXT_DIM)
    py += 14
    pasos = wi.get("steps_outside", 0)
    txt(surface, f"Pasos fuera: {pasos}", x, py, fonts["xs"], TEXT_DIM)
    py += 14
    recomp = wi.get("reward_outside", 0.0)
    txt(surface, f"Recomp fuera:{recomp:+.2f}", x, py, fonts["xs"], TEXT_DIM)
    py += 14
    py += 6
    divider(surface, x, py, w - 4)
    py += 10

    hd = status.get("home_drive", {})
    txt(surface, "Retorno a Casa", x, py, fonts["med"], ACCENT)
    py += 20
    rhr = hd.get("return_home_rate", 0.0)
    bar(
        surface,
        x,
        py,
        w - 4,
        "Tasa retorno",
        rhr,
        fonts["sm"],
        fonts["xs"],
        label_w=108,
    )
    py += 22
    txt(
        surface,
        f"En casa:  {hd.get('episodes_at_home', 0)} ep.",
        x,
        py,
        fonts["xs"],
        TEXT_DIM,
    )
    py += 14
    txt(
        surface,
        f"Fuera:    {hd.get('episodes_away', 0)} ep.",
        x,
        py,
        fonts["xs"],
        TEXT_DIM,
    )
    py += 14
    py += 6
    divider(surface, x, py, w - 4)
    py += 10

    txt(surface, "Portales (desde casa)", x, py, fonts["med"], ACCENT)
    py += 20
    portales = [
        ("Azul   → Comida  ", (50, 130, 220), "(7,2)"),
        ("Rojo   → Peligro ", (210, 50, 50), "(7,4)"),
        ("Verde  → Curiosid", (50, 200, 80), "(7,6)"),
        ("Dorado → Desafio ", (255, 200, 0), "(6,7)"),
        ("Blanco → Casa     ", (200, 200, 255), "(0,0)"),
    ]
    for label, color, pos in portales:
        txt(surface, f"  {label} {pos}", x, py, fonts["xs"], color)
        py += 13
    return py
