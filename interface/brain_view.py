"""
Panel Cerebro: visualización diagnóstica de la red DQN.
Muestra Q-values, decisión, arquitectura y activaciones.
Estos son valores matemáticos calculados — no son pensamientos reales.
"""

import pygame
from interface.ui_components import (
    txt,
    divider,
    h_bar,
    ACCENT,
    TEXT,
    TEXT_DIM,
)

_ACTION_SYMS = {
    "arriba": "^",
    "abajo": "v",
    "izquierda": "<",
    "derecha": ">",
    "esperar": ".",
}


def render(surface: pygame.Surface, fonts: dict, area: tuple, status: dict):
    x, y, w, _ = area
    py = y

    bd = status.get("brain_debug", {})
    if not bd:
        txt(surface, "Sin datos de cerebro aun", x, py, fonts["sm"], TEXT_DIM)
        py += 16
        txt(surface, "(se calcula cada 5 pasos)", x, py, fonts["xs"], TEXT_DIM)
        return py

    # ── Arquitectura ─────────────────────────────────────────────────────────
    txt(surface, "Arquitectura DQN", x, py, fonts["med"], ACCENT)
    py += 20
    layers = bd.get("layers", [])
    arch = " → ".join(str(la["size"]) for la in layers)
    txt(surface, arch, x, py, fonts["sm"], TEXT)
    py += 18
    for la in layers:
        act = la.get("activation_mean")
        if act is not None:
            line = f"  {la['name']:<10} {la['size']:>4}    act.med:{act:.4f}"
        else:
            line = f"  {la['name']:<10} {la['size']:>4} (entrada)"
        txt(surface, line, x, py, fonts["xs"], TEXT_DIM)
        py += 13
    py += 6
    divider(surface, x, py, w - 4)
    py += 10

    # ── Decisión ─────────────────────────────────────────────────────────────
    txt(surface, "Ultima decision", x, py, fonts["med"], ACCENT)
    py += 20
    dec_type = bd.get("decision_type", "?")
    if dec_type == "exploitation":
        dec_color = (100, 200, 255)
        dec_label = "explotacion  (mejor Q)"
    else:
        dec_color = (255, 180, 50)
        dec_label = "exploracion  (aleatoria)"
    txt(surface, f"Tipo:    {dec_label}", x, py, fonts["sm"], dec_color)
    py += 16
    txt(surface, f"Accion:  {bd.get('last_action', '?')}", x, py, fonts["sm"], TEXT)
    py += 16
    eps = bd.get("epsilon", 0.0)
    loss = bd.get("last_loss", 0.0)
    buf = bd.get("replay_buffer_size", 0)
    steps = bd.get("train_steps", 0)
    txt(surface, f"Epsilon: {eps:.4f}", x, py, fonts["xs"], TEXT_DIM)
    py += 14
    txt(surface, f"Loss:    {loss:.6f}", x, py, fonts["xs"], TEXT_DIM)
    py += 14
    txt(surface, f"Replay:  {buf:,}", x, py, fonts["xs"], TEXT_DIM)
    py += 14
    txt(surface, f"Pasos:   {steps:,}", x, py, fonts["xs"], TEXT_DIM)
    py += 14
    py += 6
    divider(surface, x, py, w - 4)
    py += 10

    # ── Q-values ─────────────────────────────────────────────────────────────
    txt(surface, "Q-values por accion", x, py, fonts["med"], ACCENT)
    py += 20
    qv = bd.get("q_values", {})
    best = bd.get("best_action", "")
    last_act = bd.get("last_action", "")

    if qv:
        q_vals = list(qv.values())
        q_min = min(q_vals)
        q_max = max(q_vals)
        lbl_w = 82
        bar_w = w - lbl_w - 64

        for action, q in qv.items():
            sym = _ACTION_SYMS.get(action, "?")
            is_last = action == last_act
            is_best = action == best

            a_color = ACCENT if is_last else TEXT_DIM
            # Indicador visual
            indicator = "★" if is_best else " "
            chosen = ">" if is_last else " "
            label_str = f"{chosen}{sym} {action:<11}"
            txt(surface, label_str, x, py, fonts["xs"], a_color)

            bar_color = (80, 150, 240) if is_last else (50, 65, 100)
            h_bar(
                surface,
                x + lbl_w,
                py,
                bar_w,
                q,
                q_min,
                q_max,
                color=bar_color,
                height=12,
                font_xs=fonts["xs"],
            )
            if is_best:
                txt(surface, indicator, x + w - 18, py, fonts["xs"], (255, 220, 50))
            py += 17

    return py
