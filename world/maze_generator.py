"""Generacion procedural de laberintos solucionables para BabyIA World."""

import random
from collections import deque

from world.world_config import (
    DEFAULT_GRID_SIZE,
    get_reserved_positions,
    get_key_pos,
    get_door_pos,
    get_progress_door_pos,
    get_start_pos,
)

# Compatibilidad con tests existentes (8x8 hardcodeado)
GRID_SIZE = 8
START_POS = (0, 0)
GOAL_POS = (7, 7)

_RESERVED = get_reserved_positions(DEFAULT_GRID_SIZE)


def generate_walls(
    seed: int, density: float = 0.20, grid_size: int = DEFAULT_GRID_SIZE
) -> frozenset:
    """Genera paredes aleatorias. No solapan con posiciones reservadas del grid."""
    reserved = get_reserved_positions(grid_size)
    rng = random.Random(seed)
    candidates = [
        (x, y)
        for x in range(grid_size)
        for y in range(grid_size)
        if (x, y) not in reserved
    ]
    rng.shuffle(candidates)
    count = int(len(candidates) * density)
    return frozenset(candidates[:count])


def _bfs_reachable(
    start: tuple, goal: tuple, blocked: frozenset, grid_size: int = DEFAULT_GRID_SIZE
) -> bool:
    """True si goal es alcanzable desde start sin cruzar celdas bloqueadas."""
    if start == goal:
        return True
    visited = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nx, ny = x + dx, y + dy
            npos = (nx, ny)
            if (
                0 <= nx < grid_size
                and 0 <= ny < grid_size
                and npos not in blocked
                and npos not in visited
            ):
                if npos == goal:
                    return True
                visited.add(npos)
                queue.append(npos)
    return False


def is_solvable(
    walls: frozenset,
    start: tuple = START_POS,
    goal: tuple = GOAL_POS,
    grid_size: int = DEFAULT_GRID_SIZE,
) -> bool:
    """BFS simple: True si existe camino de start a goal sin cruzar paredes."""
    return _bfs_reachable(start, goal, walls, grid_size)


def is_solvable_with_key_door(
    walls: frozenset,
    start: tuple | None = None,
    key_pos: tuple | None = None,
    door_pos: tuple | None = None,
    goal: tuple | None = None,
    grid_size: int = DEFAULT_GRID_SIZE,
) -> bool:
    """
    BFS por etapas: valida que el laberinto sea solucionable teniendo en cuenta
    que la puerta solo se abre con llave.

    Etapa 1: start -> key_pos  (puerta sigue cerrada = bloqueante)
    Etapa 2: key_pos -> goal   (puerta abierta = pasable, solo paredes bloquean)
    """
    gs = grid_size
    _start = start if start is not None else get_start_pos(gs)
    _key = key_pos if key_pos is not None else get_key_pos(gs)
    _door = door_pos if door_pos is not None else get_door_pos(gs)
    _goal = goal if goal is not None else get_progress_door_pos(gs)

    blocked_no_key = walls | {_door}
    if not _bfs_reachable(_start, _key, blocked_no_key, gs):
        return False
    return _bfs_reachable(_key, _goal, walls, gs)


def generate_solvable_maze(
    seed: int,
    density: float = 0.20,
    max_attempts: int = 50,
    grid_size: int = DEFAULT_GRID_SIZE,
) -> tuple[frozenset, int]:
    """
    Genera un laberinto solucionable (BFS simple).
    Devuelve (walls, seed_efectivo); en caso extremo devuelve sin paredes.
    """
    gs = grid_size
    _start = get_start_pos(gs)
    _goal = get_progress_door_pos(gs)
    for offset in range(max_attempts):
        candidate = seed + offset
        walls = generate_walls(candidate, density, gs)
        if is_solvable(walls, _start, _goal, gs):
            return walls, candidate
    return frozenset(), seed


def generate_solvable_maze_with_key_door(
    seed: int,
    density: float = 0.20,
    max_attempts: int = 50,
    grid_size: int = DEFAULT_GRID_SIZE,
) -> tuple[frozenset, int]:
    """
    Genera un laberinto solucionable con validacion llave-puerta (BFS por etapas).
    Devuelve (walls, seed_efectivo); en caso extremo devuelve sin paredes.
    """
    for offset in range(max_attempts):
        candidate = seed + offset
        walls = generate_walls(candidate, density, grid_size)
        if is_solvable_with_key_door(walls, grid_size=grid_size):
            return walls, candidate
    return frozenset(), seed
