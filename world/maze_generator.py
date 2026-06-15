"""Generacion procedural de laberintos solucionables para BabyIA World."""
import random
from collections import deque

GRID_SIZE = 8
START_POS = (0, 0)
GOAL_POS  = (7, 7)

# Posiciones fijas de objetos y entradas/salidas: nunca seran pared
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


def _bfs_reachable(start: tuple, goal: tuple, blocked: frozenset) -> bool:
    """True si goal es alcanzable desde start sin cruzar celdas bloqueadas."""
    if start == goal:
        return True
    visited = {start}
    queue   = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nx, ny = x + dx, y + dy
            npos   = (nx, ny)
            if (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE
                    and npos not in blocked and npos not in visited):
                if npos == goal:
                    return True
                visited.add(npos)
                queue.append(npos)
    return False


def is_solvable(walls: frozenset, start: tuple = START_POS,
                goal: tuple = GOAL_POS) -> bool:
    """BFS simple: True si existe camino de start a goal sin cruzar paredes."""
    return _bfs_reachable(start, goal, walls)


def is_solvable_with_key_door(walls: frozenset,
                               start: tuple = START_POS,
                               key_pos: tuple = (1, 6),
                               door_pos: tuple = (3, 6),
                               goal: tuple = GOAL_POS) -> bool:
    """
    BFS por etapas: valida que el laberinto sea solucionable teniendo en cuenta
    que la puerta solo se abre con llave.

    Etapa 1: start -> key_pos  (puerta sigue cerrada = bloqueante)
    Etapa 2: key_pos -> goal   (puerta abierta = pasable, solo paredes bloquean)
    """
    # Sin llave, la puerta actua como pared
    blocked_no_key = walls | {door_pos}
    if not _bfs_reachable(start, key_pos, blocked_no_key):
        return False
    # Con llave, la puerta ya no bloquea
    return _bfs_reachable(key_pos, goal, walls)


def generate_solvable_maze(seed: int, density: float = 0.20,
                            max_attempts: int = 50) -> tuple[frozenset, int]:
    """
    Genera un laberinto solucionable (BFS simple).
    Devuelve (walls, seed_efectivo); en caso extremo devuelve sin paredes.
    """
    for offset in range(max_attempts):
        candidate = seed + offset
        walls = generate_walls(candidate, density)
        if is_solvable(walls):
            return walls, candidate
    return frozenset(), seed


def generate_solvable_maze_with_key_door(seed: int, density: float = 0.20,
                                          max_attempts: int = 50) -> tuple[frozenset, int]:
    """
    Genera un laberinto solucionable con validacion llave-puerta (BFS por etapas).
    Devuelve (walls, seed_efectivo); en caso extremo devuelve sin paredes.
    """
    for offset in range(max_attempts):
        candidate = seed + offset
        walls = generate_walls(candidate, density)
        if is_solvable_with_key_door(walls):
            return walls, candidate
    return frozenset(), seed
