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
