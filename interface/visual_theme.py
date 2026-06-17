"""
interface/visual_theme.py — Paleta de colores y utilidades visuales para BabyIA 0.4.4.

Centraliza constantes de color por mision, estado y tipo de celda.
No contiene logica de entrenamiento.
"""

# ── Colores de mision ─────────────────────────────────────────────────────────

MISSION_COLORS = {
    "FIND_KEY": (255, 220, 60),  # amarillo — buscar llave
    "GO_TO_NEXT_LEVEL_DOOR": (255, 185, 0),  # dorado — ir a puerta progreso
    "AVOID_DANGER": (220, 60, 60),  # rojo — evitar peligro
    "COLLECT_USEFUL_POWERUP": (60, 210, 240),  # cian — powerup util
    "RETURN_HOME": (120, 180, 255),  # azul — volver a casa
    "LEVEL_COMPLETED": (80, 255, 120),  # verde brillante — nivel completado
    "EXPLORE_OPTIONAL_ROOM": (50, 220, 180),  # turquesa — sala opcional
}

# ── Colores de distancia / proximidad ─────────────────────────────────────────

NEAR_COLOR = (80, 220, 80)  # verde — objetivo cerca
MID_COLOR = (220, 180, 50)  # amarillo — a media distancia
FAR_COLOR = (180, 80, 80)  # rojo — lejos del objetivo

# ── Colores de estado corporal relevantes ─────────────────────────────────────

ENERGY_HIGH = (80, 220, 120)
ENERGY_LOW = (220, 80, 80)
SHIELD_COLOR = (80, 140, 255)

# ── Utiles ────────────────────────────────────────────────────────────────────


def mission_color(goal: str) -> tuple:
    """Devuelve el color RGB asociado a un estado de mision."""
    return MISSION_COLORS.get(goal, (200, 200, 200))


def distance_color(dist_normalized: float) -> tuple:
    """Devuelve color segun distancia normalizada (0=cerca, 1=lejos)."""
    if dist_normalized < 0.3:
        return NEAR_COLOR
    if dist_normalized < 0.6:
        return MID_COLOR
    return FAR_COLOR


def energy_color(energy: float) -> tuple:
    """Devuelve color segun nivel de energia (0-1)."""
    return ENERGY_HIGH if energy >= 0.4 else ENERGY_LOW


def blend_color(c1: tuple, c2: tuple, t: float) -> tuple:
    """Interpola linealmente entre dos colores RGB."""
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
