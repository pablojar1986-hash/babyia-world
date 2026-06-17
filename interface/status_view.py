"""Panel Estado: episodio, nivel, recompensa, emociones y laberinto."""

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

    mode_str = status.get("mode", "train").upper()
    mode_color = {
        "TRAIN": (100, 200, 100),
        "WATCH": (100, 170, 255),
        "EVALUATE": (255, 180, 50),
    }.get(mode_str, ACCENT)
    txt(surface, f"● {mode_str}", x, py, fonts["xs"], mode_color)
    py += 16
    divider(surface, x, py, w - 4)
    py += 10

    txt(surface, f"Episodio : {status['episode']}", x, py, fonts["med"], TEXT)
    py += 19
    txt(surface, f"Nivel    : {status['level']}", x, py, fonts["med"], TEXT)
    py += 19
    txt(surface, f"Epsilon  : {status['epsilon']:.4f}", x, py, fonts["sm"], TEXT_DIM)
    py += 16
    ep_r = status.get("episode_reward", 0.0)
    txt(
        surface,
        f"Recomp.  : {ep_r:+.2f}",
        x,
        py,
        fonts["sm"],
        COLOR_POS if ep_r >= 0 else COLOR_NEG,
    )
    py += 16
    txt(
        surface,
        f"Exito 20ep: {status.get('success_rate', 0.0) * 100:.0f}%",
        x,
        py,
        fonts["sm"],
        TEXT,
    )
    py += 16

    # 0.4.3: objetivo actual, llave e inventario
    obj = status.get("current_objective", "")
    if obj:
        obj_c = (
            (255, 215, 0) if "dorada" in obj or "completado" in obj.lower() else TEXT
        )
        txt(surface, f"Obj: {obj[:28]}", x, py, fonts["xs"], obj_c)
        py += 14
    has_key = status.get("has_key", False)
    key_c = (80, 220, 80) if has_key else (180, 60, 60)
    key_label = "Llave: SI" if has_key else "Llave: NO"
    txt(surface, key_label, x, py, fonts["xs"], key_c)
    py += 14

    ewp = status.get("episodes_without_progress", 0)
    lc = status.get("level_completions", 0)
    stag = status.get("stagnation_active", False)
    if stag:
        if ewp > 500:
            stag_label, stag_c = f"CRITICO {ewp}ep", (255, 60, 60)
        elif ewp > 300:
            stag_label, stag_c = f"Severo {ewp}ep", (240, 100, 40)
        elif ewp > 200:
            stag_label, stag_c = f"Moderado {ewp}ep", (220, 160, 30)
        else:
            stag_label, stag_c = f"Leve {ewp}ep", (180, 180, 60)
        txt(surface, f"Estancado: {stag_label}", x, py, fonts["xs"], stag_c)
    else:
        txt(surface, f"Sin progreso: {ewp} ep.", x, py, fonts["xs"], TEXT_DIM)
    py += 14
    cur = status.get("curriculum", {})
    req = cur.get("required", 0)
    txt(
        surface,
        f"Completados: {lc}/{req}",
        x,
        py,
        fonts["xs"],
        (100, 220, 100) if lc >= req else TEXT_DIM,
    )
    py += 14
    avg_r = status.get("avg_reward")
    avg_s = status.get("avg_steps")
    if avg_r is not None:
        txt(surface, f"Prom recomp: {avg_r:+.2f}", x, py, fonts["xs"], TEXT_DIM)
        py += 14
    if avg_s is not None:
        txt(surface, f"Prom pasos : {avg_s:.0f}", x, py, fonts["xs"], TEXT_DIM)
        py += 14
    py += 6
    divider(surface, x, py, w - 4)
    py += 10

    txt(surface, "Senales internas", x, py, fonts["med"], ACCENT)
    py += 20
    em = status.get("emotions", {})
    for label, key, warn in [
        ("Curiosidad", "curiosity", None),
        ("Confianza", "confidence", None),
        ("Frustracion", "frustration", 0.6),
        ("Energia int.", "energy", None),
    ]:
        bar(
            surface,
            x,
            py,
            w - 4,
            label,
            em.get(key, 0.5),
            fonts["sm"],
            fonts["xs"],
            warn,
            label_w=108,
        )
        py += 22
    py += 6
    divider(surface, x, py, w - 4)
    py += 10

    txt(surface, "Laberinto", x, py, fonts["med"], ACCENT)
    py += 20
    maze = status.get("maze_info", {})
    txt(
        surface,
        f"Nivel:    {maze.get('difficulty', 'Basico')}",
        x,
        py,
        fonts["sm"],
        TEXT,
    )
    py += 16
    txt(surface, f"Semilla:  {maze.get('seed', 0)}", x, py, fonts["xs"], TEXT_DIM)
    py += 14
    solv = maze.get("solvable", True)
    txt(
        surface,
        f"Solucion: {'OK' if solv else 'NO'}",
        x,
        py,
        fonts["xs"],
        (100, 220, 100) if solv else (220, 90, 90),
    )
    py += 14
    return py
