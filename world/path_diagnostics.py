"""
world/path_diagnostics.py — Diagnostico de rutas BFS para BabyIA World 0.4.6b.

Verifica si existe ruta accesible desde la posicion actual hasta la llave
y desde la llave hasta la puerta de progreso.
No contiene logica de entrenamiento — solo consulta el estado del mundo.
"""

from __future__ import annotations

from collections import deque


def _bfs(world, start: tuple, goal: tuple, has_key: bool = False):
    """
    BFS sobre el grid. Devuelve (distancia, camino) o (None, []).
    Trata paredes y DOOR_CLOSED-sin-llave como celdas bloqueadas.
    """
    if start == goal:
        return 0, [start]

    visited = {start}
    queue = deque([(start, [start])])

    while queue:
        (cx, cy), path = queue.popleft()
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nx, ny = cx + dx, cy + dy
            npos = (nx, ny)
            if npos in visited:
                continue
            if not world._is_passable([nx, ny], has_key):
                continue
            new_path = path + [npos]
            if npos == goal:
                return len(path), new_path
            visited.add(npos)
            queue.append((npos, new_path))

    return None, []


def check_path_to_key_and_door(world) -> dict:
    """
    Analiza la accesibilidad de llave y puerta desde la posicion actual.

    Devuelve un dict con:
        route_to_key_exists           bool
        route_key_to_door_exists      bool
        shortest_distance_to_key      int | None
        shortest_distance_key_to_door int | None
        hazards_on_route              int
        walls_blocking                int
        key_reachable                 bool
        progress_door_reachable_after_key bool
    """
    start = tuple(world.baby_pos)
    key_pos = tuple(world.key_pos)
    door_pos = tuple(world.progress_door_pos)
    hazard_positions = set(getattr(world, "_hazard_positions", {}).keys())

    # Ruta baby -> llave (sin llave todavia)
    dist_to_key, path_to_key = _bfs(world, start, key_pos, has_key=False)

    # Ruta llave -> puerta (ya con llave)
    dist_key_to_door, path_key_to_door = _bfs(world, key_pos, door_pos, has_key=True)

    # Hazards en ambas rutas combinadas
    all_route_cells = set(path_to_key) | set(path_key_to_door)
    hazards_on_route = len(all_route_cells & hazard_positions)

    # Paredes que bloquean (solo si la ruta no existe — cuenta muros en area directa)
    walls_blocking = 0
    if dist_to_key is None:
        bx, by = start
        kx, ky = key_pos
        for y in range(min(by, ky), max(by, ky) + 1):
            for x in range(min(bx, kx), max(bx, kx) + 1):
                if 0 <= y < world.size and 0 <= x < world.size:
                    if (x, y) in world.walls:
                        walls_blocking += 1

    return {
        "route_to_key_exists": dist_to_key is not None,
        "route_key_to_door_exists": dist_key_to_door is not None,
        "shortest_distance_to_key": dist_to_key,
        "shortest_distance_key_to_door": dist_key_to_door,
        "hazards_on_route": hazards_on_route,
        "walls_blocking": walls_blocking,
        "key_reachable": dist_to_key is not None,
        "progress_door_reachable_after_key": dist_key_to_door is not None,
    }
