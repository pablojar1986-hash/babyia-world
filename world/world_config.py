"""
world/world_config.py — Configuracion de mundo escalable para BabyIA 0.4.5.

Centraliza tamanos de grid y posiciones de objetos para distintos niveles.
Todas las posiciones se derivan de formulas validadas para grid 8x8.
"""

from __future__ import annotations

DEFAULT_GRID_SIZE = 8
MIN_GRID_SIZE = 8
MAX_GRID_SIZE = 16
VIEWPORT_SIZE = 8  # celdas visibles en pantalla (puede ser < grid_size)
DEFAULT_VISION_RANGE = 3  # rango de vision de PerceptionSystem

_LEVEL_SIZES: dict[int, int] = {
    0: 8,
    1: 10,
    2: 12,
    3: 14,
    4: 16,
    5: 16,
    6: 16,
}


def get_grid_size_for_level(level: int) -> int:
    """Devuelve el tamano de grid para el nivel. Maximo 16."""
    return _LEVEL_SIZES.get(level, MAX_GRID_SIZE)


# ── Posiciones derivadas de formulas validadas para gs=8 ─────────────────────
# Verificacion gs=8: todas coinciden con las constantes hardcodeadas previas.


def get_start_pos(gs: int) -> tuple:
    return (0, 0)


def get_key_pos(gs: int) -> tuple:
    """Llave cerca del borde inferior-izquierdo. gs=8 → (1,6) ✓"""
    return (1, gs - 2)


def get_door_pos(gs: int) -> tuple:
    """Puerta normal en la misma fila que la llave. gs=8 → (3,6) ✓"""
    return (gs // 2 - 1, gs - 2)


def get_food_pos(gs: int) -> tuple:
    """Comida en zona media-derecha. gs=8 → (6,2) ✓"""
    return (gs - 2, gs // 4)


def get_danger_pos(gs: int) -> tuple:
    """Peligro basico en zona central. gs=8 → (3,5) ✓"""
    return (gs // 2 - 1, gs - 3)


def get_unknown_pos(gs: int) -> tuple:
    """Objeto desconocido en borde derecho-alto. gs=8 → (7,1) ✓"""
    return (gs - 1, 1)


def get_progress_door_pos(gs: int) -> tuple:
    """Puerta de progreso (next_level_door) en esquina inferior-derecha. gs=8 → (7,7) ✓"""
    return (gs - 1, gs - 1)


def get_training_door_pos(gs: int) -> tuple:
    """Sala de entrenamiento en esquina superior-derecha. gs=8 → (7,0) ✓"""
    return (gs - 1, 0)


def get_treasure_door_pos(gs: int) -> tuple:
    """Sala del tesoro en borde inferior-central. gs=8 → (4,7) ✓"""
    return (gs // 2, gs - 1)


def get_powerup_positions(gs: int) -> dict:
    """
    Powerups escalados al tamano del grid.
    gs=8 → {(0,3):'growth_crystal', (4,0):'shield_orb', (6,5):'energy_food', (1,5):'speed_boots'} ✓
    """
    return {
        (0, gs // 2 - 1): "growth_crystal",
        (gs // 2, 0): "shield_orb",
        (gs - 2, gs - 3): "energy_food",
        (1, gs - 3): "speed_boots",
    }


def get_hazard_positions(gs: int) -> dict:
    """
    Hazards escalados al tamano del grid.
    gs=8 → {(1,2):'fire_zone', (0,6):'spikes', (6,3):'mud'} ✓
    """
    return {
        (1, gs // 4): "fire_zone",
        (0, gs - 2): "spikes",
        (gs - 2, gs // 2 - 1): "mud",
    }


def get_special_door_positions(gs: int) -> dict:
    """
    Puertas especiales escaladas.
    gs=8 → {(3,0):'heavy_door', (5,2):'small_door'} ✓
    """
    return {
        (gs // 2 - 1, 0): "heavy_door",
        (gs // 2 + 1, gs // 4): "small_door",
    }


def get_reserved_positions(gs: int) -> frozenset:
    """Posiciones que nunca pueden ser pared (objetos clave del nivel)."""
    return frozenset(
        [
            get_start_pos(gs),
            get_progress_door_pos(gs),
            get_key_pos(gs),
            get_door_pos(gs),
            get_food_pos(gs),
            get_danger_pos(gs),
            get_unknown_pos(gs),
        ]
    )
