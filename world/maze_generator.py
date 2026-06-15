"""Generacion procedural de laberintos solucionables para BabyIA World."""
import random
from collections import deque

GRID_SIZE = 8
START_POS = (0, 0)
GOAL_POS  = (7, 7)

# Posiciones reservadas: nunca seran pared
_RESERVED = frozenset([
    START_POS, GOAL_POS,
    (1, 6),   # KEY
    (3, 6),   # DOOR
    (6, 2),   # FOOD
    (3, 5),   # DANGER
    (7, 1),   # UNKNOWN
])


def generate_walls(seed: int, density: float = 0.20) -> frozenset:
    """Genera paredes aleatorias usando semilla. No solapan con posiciones reservadas."""
    rng = random.Random(seed)
    candidates = [
        (x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)
        if (x, y) not in _RESERVED
    ]
    rng.shuffle(candidates)
    count = int(len(candidates) * density)
    return frozenset(candidates[:count])


def is_solvable(walls: frozenset, start: tuple = START_POS,
                goal: tuple = GOAL_POS) -> bool:
    """BFS: devuelve True si existe camino de start a goal sin cruzar paredes."""
    visited = {start}
    queue   = deque([start])
    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            return True
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nx, ny = x + dx, y + dy
            npos   = (nx, ny)
            if (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE
                    and npos not in walls and npos not in visited):
                visited.add(npos)
                queue.append(npos)
    return False


def generate_solvable_maze(seed: int, density: float = 0.20,
                            max_attempts: int = 50) -> tuple[frozenset, int]:
    """
    Genera un laberinto solucionable. Devuelve (walls, seed_efectivo).
    Prueba hasta max_attempts semillas; en caso extremo devuelve sin paredes.
    """
    for offset in range(max_attempts):
        candidate = seed + offset
        walls = generate_walls(candidate, density)
        if is_solvable(walls):
            return walls, candidate
    return frozenset(), seed
