"""Fabrica de laberintos progresivos por nivel para BabyIA World 0.2.2."""
import json
from pathlib import Path

from config import DATA_DIR
from world.maze_generator import (
    generate_solvable_maze,
    generate_solvable_maze_with_key_door,
    is_solvable,
    is_solvable_with_key_door,
)

LEVEL_STATS_FILE = DATA_DIR / "level_stats.json"

# Paredes base del mundo 0.2 — se usan en nivel 1
BASE_WALLS = frozenset({
    (2, 0), (2, 1), (2, 2), (2, 3),
    (5, 4), (5, 5), (5, 6), (5, 7),
    (4, 2), (3, 4),
})

# nivel -> (densidad, semilla_base, etiqueta_dificultad, descripcion)
_CONFIGS: dict[int, tuple] = {
    0: (0.00,   0, "Tutorial", "mundo completamente abierto, sin paredes"),
    1: (0.00,   0, "Basico",   "paredes fijas del mundo base"),
    2: (0.15,  42, "Facil",    "laberinto ligero generado"),
    3: (0.20,  99, "Medio",    "laberinto moderado"),
    4: (0.25, 137, "Dificil",  "laberinto denso, requiere llave y puerta"),
    5: (0.30, 256, "Experto",  "laberinto complejo, requiere llave y puerta"),
    6: (0.35, 512, "Maestro",  "laberinto extremo, requiere llave y puerta"),
}

# Niveles que requieren validacion llave->puerta->meta
_KEY_DOOR_LEVELS = frozenset({4, 5, 6})


def get_maze_for_level(level: int) -> dict:
    """
    Devuelve configuracion de laberinto para el nivel (0-6).

    Nivel 0: mundo completamente abierto (sin paredes).
    Nivel 1: paredes fijas BASE_WALLS.
    Niveles 2-3: generacion procedural con BFS simple.
    Niveles 4-6: generacion procedural con BFS llave->puerta->meta.
    """
    level = max(0, min(level, 6))
    density, base_seed, difficulty, description = _CONFIGS[level]
    requires_key_door = level in _KEY_DOOR_LEVELS

    if level == 0:
        walls, seed = frozenset(), base_seed
        solvable = True
    elif level == 1:
        walls, seed = BASE_WALLS, base_seed
        solvable = is_solvable(walls)
    elif requires_key_door:
        walls, seed = generate_solvable_maze_with_key_door(base_seed, density)
        solvable = is_solvable_with_key_door(walls)
    else:
        walls, seed = generate_solvable_maze(base_seed, density)
        solvable = is_solvable(walls)

    return {
        "level"           : level,
        "walls"           : walls,
        "seed"            : seed,
        "density"         : density,
        "difficulty"      : difficulty,
        "solvable"        : solvable,
        "description"     : description,
        "wall_count"      : len(walls),
        "requires_key_door": requires_key_door,
    }


def save_level_stats(maze_info: dict, stats_file: Path | None = None):
    """Persiste informacion del nivel actual en data/level_stats.json."""
    path = Path(stats_file) if stats_file else LEVEL_STATS_FILE
    path.parent.mkdir(exist_ok=True)
    payload = {
        k: (sorted(v) if isinstance(v, frozenset) else v)
        for k, v in maze_info.items()
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_level_stats(stats_file: Path | None = None) -> dict:
    """Carga informacion de nivel guardada previamente. Devuelve {} si no existe."""
    path = Path(stats_file) if stats_file else LEVEL_STATS_FILE
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
