"""Panel Memoria: conceptos, memoria causal y bitácora."""

from interface.ui_components import (
    txt,
    divider,
    ACCENT,
    TEXT_DIM,
)


def render(surface, fonts, area, status):
    x, y, w, _ = area
    py = y

    txt(surface, "Conceptos descubiertos", x, py, fonts["med"], ACCENT)
    py += 20
    top_c = status.get("concepts", [])
    if top_c:
        for c in top_c[:4]:
            rel = f"{c['relation']}:{c['value']}"[:30]
            conf = c["confidence"]
            txt(surface, f"  {rel}", x, py, fonts["xs"], (130, 210, 140))
            py += 13
            txt(surface, f"    confianza={conf:.2f}", x, py, fonts["xs"], TEXT_DIM)
            py += 13
    else:
        txt(surface, "  Ninguno aun", x, py, fonts["xs"], TEXT_DIM)
        py += 14
    py += 6
    divider(surface, x, py, w - 4)
    py += 10

    causal = status.get("causal_learned", 0)
    txt(surface, "Memoria Causal", x, py, fonts["med"], ACCENT)
    py += 20
    c_color = (100, 220, 100) if causal >= 3 else TEXT_DIM
    txt(surface, f"Relaciones aprendidas: {causal}", x, py, fonts["sm"], c_color)
    py += 16
    txt(surface, "(conf >= 60%,  min 3 obs)", x, py, fonts["xs"], TEXT_DIM)
    py += 14
    py += 6
    divider(surface, x, py, w - 4)
    py += 10

    txt(surface, "Inventario", x, py, fonts["med"], ACCENT)
    py += 20
    inv = status.get("inventory", {})
    key_c = (255, 220, 80) if inv.get("has_key") else TEXT_DIM
    txt(
        surface,
        f"Llave: {'SI' if inv.get('has_key') else 'NO'}",
        x,
        py,
        fonts["sm"],
        key_c,
    )
    py += 16
    energy = inv.get("energy", 1.0)
    from interface.ui_components import bar

    bar(
        surface,
        x,
        py,
        w - 4,
        "Energia",
        energy,
        fonts["sm"],
        fonts["xs"],
        warn_at=0.3,
        label_w=80,
    )
    py += 22
    txt(
        surface,
        f"Comida consumida: {inv.get('food_count', 0)}",
        x,
        py,
        fonts["xs"],
        TEXT_DIM,
    )
    py += 14
    py += 6
    divider(surface, x, py, w - 4)
    py += 10

    txt(surface, "Bitacora reciente", x, py, fonts["med"], ACCENT)
    py += 20
    for entry in status.get("last_log", [])[-7:]:
        line = entry[:44]
        txt(surface, line, x, py, fonts["xs"], TEXT_DIM)
        py += 14
    return py
