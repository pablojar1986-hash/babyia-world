import numpy as np
from world.objects import Cell, GRID_SIZE
from world.rewards import calculate_reward
from world.level_doors import (
    LEVEL_DOOR_POSITIONS,
    LEVEL_DOOR_TYPES,
    attempt_level_door,
    is_progress_door,
)

# Barreras + obstaculos aislados (identicos a 0.1.x)
WALL_POSITIONS = frozenset(
    {
        (2, 0),
        (2, 1),
        (2, 2),
        (2, 3),  # barrera izquierda
        (5, 4),
        (5, 5),
        (5, 6),
        (5, 7),  # barrera derecha
        (4, 2),
        (3, 4),  # obstaculos aislados
    }
)

# Objetos interactivos (0.2). Posiciones que no solapan con paredes.
OBJECT_POSITIONS: dict[tuple, Cell] = {
    (1, 6): Cell.KEY,
    (3, 6): Cell.DOOR_CLOSED,
    (6, 2): Cell.FOOD,
    (3, 5): Cell.DANGER,
    (7, 1): Cell.UNKNOWN_OBJECT,
}

# 0.4.2: powerups recogibles (se agotan al pisar). Coordenadas (col, row).
POWERUP_POSITIONS: dict[tuple, str] = {
    (0, 3): "growth_crystal",
    (4, 0): "shield_orb",
    (6, 5): "energy_food",
    (1, 5): "speed_boots",
}

# 0.4.2: hazards persistentes (siempre activos). Coordenadas (col, row).
HAZARD_POSITIONS: dict[tuple, str] = {
    (1, 2): "fire_zone",
    (0, 6): "spikes",
    (6, 3): "mud",
}

# 0.4.2: puertas especiales con requisito corporal. Coordenadas (col, row).
SPECIAL_DOOR_POSITIONS: dict[tuple, str] = {
    (3, 0): "heavy_door",
    (5, 2): "small_door",
}

# 0.4.3: la posicion (7,7) es ahora NEXT_LEVEL_DOOR (ver LEVEL_DOOR_POSITIONS).
# GOAL_POS se mantiene para compatibilidad visual.
GOAL_POS = (7, 7)
START_POS = (0, 0)
MAX_STEPS = 200

_BASE_OBS = 10


class GridWorld:
    def __init__(self):
        self.size = GRID_SIZE
        self.goal = GOAL_POS
        self.walls = WALL_POSITIONS
        self.reset()

    # ── Control de episodio ────────────────────────────────────────────────────

    def reset(self) -> np.ndarray:
        self.baby_pos = list(START_POS)
        self.steps = 0
        self.visited = {START_POS}
        self.action_history: list[int] = []
        self.last_reward = 0.0
        self.hit_wall = False
        self.done = False
        # Estado mutable de objetos
        self.key_present = (1, 6) in OBJECT_POSITIONS
        self.door_open = False
        self.food_present = (6, 2) in OBJECT_POSITIONS
        self.unknown_touched = False
        # 0.4.2: powerups restantes (se consumen al recoger)
        self._remaining_powerups: dict[tuple, str] = dict(POWERUP_POSITIONS)
        return self._get_observation()

    # ── Paso de simulacion ────────────────────────────────────────────────────

    def step(self, action: int, has_key: bool = False):
        """
        Ejecuta un paso. has_key indica si BabyIA lleva llave.
        Devuelve (obs, reward, done, info).
        """
        if self.done:
            return self._get_observation(), 0.0, True, {}

        self.steps += 1
        action = int(action)
        new_pos = self._apply_action(action)
        self.action_history.append(action)

        hit_wall = False
        visited_new = False
        reached_goal = False
        info_obj: dict = {
            "hit_wall": False,
            "reached_goal": False,
            "visited_new": False,
            "steps": self.steps,
            "hit_door_closed": False,
            "picked_key": False,
            "opened_door": False,
            "ate_food": False,
            "in_danger": False,
            "found_unknown": False,
            "hit_powerup": None,
            "hit_hazard": None,
            "hit_special_door": None,
            # 0.4.3: puertas de nivel
            "level_completed": False,
            "next_level_door_opened": False,
            "hit_next_level_door": False,
            "entered_optional_room": None,
            "entered_treasure_room": False,
            "entered_training_room": False,
            "wrong_door": False,
            "missing_requirement": "",
        }

        cell_at = self._cell_at(new_pos)
        pos_t = tuple(new_pos)

        # 0.4.3: detectar colision con puerta de siguiente nivel SIN llave
        level_door_id = LEVEL_DOOR_POSITIONS.get(pos_t)
        next_level_blocked = (
            level_door_id is not None
            and is_progress_door(level_door_id)
            and not has_key
        )

        if self._is_passable(new_pos, has_key) and not next_level_blocked:
            self.baby_pos = list(new_pos)

            if pos_t not in self.visited:
                visited_new = True
                self.visited.add(pos_t)

            # Interacciones con objetos del mundo (0.2)
            if cell_at == Cell.DOOR_CLOSED and has_key:
                self.door_open = True
                info_obj["opened_door"] = True
            elif cell_at == Cell.KEY and self.key_present:
                self.key_present = False
                info_obj["picked_key"] = True
            elif cell_at == Cell.FOOD and self.food_present:
                self.food_present = False
                info_obj["ate_food"] = True
            elif cell_at == Cell.DANGER:
                info_obj["in_danger"] = True
            elif cell_at == Cell.UNKNOWN_OBJECT and not self.unknown_touched:
                self.unknown_touched = True
                info_obj["found_unknown"] = True

            # 0.4.2: powerups recogibles, hazards, puertas especiales
            pu = self._remaining_powerups.get(pos_t)
            if pu:
                del self._remaining_powerups[pos_t]
                info_obj["hit_powerup"] = pu
            hz = HAZARD_POSITIONS.get(pos_t)
            if hz:
                info_obj["hit_hazard"] = hz
            sd = SPECIAL_DOOR_POSITIONS.get(pos_t)
            if sd:
                info_obj["hit_special_door"] = sd

            # 0.4.3: puertas de nivel
            if level_door_id:
                result = attempt_level_door(level_door_id, has_key)
                door_def = LEVEL_DOOR_TYPES[level_door_id]
                if result["level_completed"]:
                    info_obj["level_completed"] = True
                    info_obj["next_level_door_opened"] = True
                    reached_goal = True  # compatibilidad con tests existentes
                    self.done = True
                elif door_def.door_type == "treasure":
                    info_obj["entered_optional_room"] = level_door_id
                    info_obj["entered_treasure_room"] = True
                elif door_def.door_type == "training_room":
                    info_obj["entered_optional_room"] = level_door_id
                    info_obj["entered_training_room"] = True
        else:
            hit_wall = True
            if cell_at == Cell.DOOR_CLOSED:
                info_obj["hit_door_closed"] = True
            # 0.4.3: intento de cruzar puerta de progreso sin llave
            if next_level_blocked:
                info_obj["hit_next_level_door"] = True
                info_obj["missing_requirement"] = "necesita llave"
                hit_wall = False  # no es choque de pared, es bloqueo de puerta

        self.hit_wall = hit_wall
        if self.steps >= MAX_STEPS:
            self.done = True

        reward = calculate_reward(
            hit_wall, reached_goal, visited_new, self.action_history
        )
        self.last_reward = reward

        info_obj["hit_wall"] = hit_wall
        info_obj["reached_goal"] = reached_goal
        info_obj["visited_new"] = visited_new

        return self._get_observation(), reward, self.done, info_obj

    # ── Consultas del estado del mundo ────────────────────────────────────────

    def get_object_state(self) -> dict:
        """Exporta posiciones y estados de objetos para el Trainer."""
        return {
            "key_pos": (1, 6),
            "key_present": self.key_present,
            "door_pos": (3, 6),
            "door_open": self.door_open,
            "food_pos": (6, 2),
            "food_present": self.food_present,
            "danger_pos": (3, 5),
            "unknown_pos": (7, 1),
        }

    def danger_nearby(self) -> bool:
        """True si hay una zona peligrosa adyacente (4 vecinos)."""
        bx, by = self.baby_pos
        danger_pos = (3, 5)
        dx, dy = danger_pos
        return abs(bx - dx) + abs(by - dy) <= 1

    def get_nearby_level_door(self) -> str | None:
        """
        Devuelve el id de la puerta de nivel adyacente (8 vecinos), o None.
        Distingue entre puertas de progreso y opcionales.
        """
        bx, by = self.baby_pos
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                p = (bx + dx, by + dy)
                if p in LEVEL_DOOR_POSITIONS:
                    return LEVEL_DOOR_POSITIONS[p]
        return None

    def get_nearby_progress_door(self) -> bool:
        """True si la puerta de siguiente nivel esta adyacente (8 vecinos)."""
        bx, by = self.baby_pos
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                p = (bx + dx, by + dy)
                door_id = LEVEL_DOOR_POSITIONS.get(p)
                if door_id and is_progress_door(door_id):
                    return True
        return False

    def get_grid(self) -> np.ndarray:
        """Matriz 2D para el renderizador (fila=Y, col=X)."""
        grid = np.zeros((self.size, self.size), dtype=int)
        for wx, wy in self.walls:
            grid[wy][wx] = int(Cell.WALL)
        # 0.4.3: GOAL visual solo si no fue reemplazado por puerta de nivel
        gx, gy = self.goal
        grid[gy][gx] = int(Cell.GOAL)
        # Objetos dinamicos basicos (0.2)
        if self.key_present:
            grid[6][1] = int(Cell.KEY)
        door_state = Cell.DOOR_OPEN if self.door_open else Cell.DOOR_CLOSED
        grid[6][3] = int(door_state)
        if self.food_present:
            grid[2][6] = int(Cell.FOOD)
        grid[5][3] = int(Cell.DANGER)
        grid[1][7] = int(Cell.UNKNOWN_OBJECT)
        # 0.4.2: powerups restantes, hazards, puertas especiales
        for px, py in self._remaining_powerups:
            grid[py][px] = int(Cell.POWERUP)
        for hx, hy in HAZARD_POSITIONS:
            grid[hy][hx] = int(Cell.HAZARD)
        for sdx, sdy in SPECIAL_DOOR_POSITIONS:
            grid[sdy][sdx] = int(Cell.SPECIAL_DOOR)
        # 0.4.3: puertas de nivel (sobreescriben GOAL visual)
        for (ldx, ldy), door_id in LEVEL_DOOR_POSITIONS.items():
            cell_type = (
                Cell.LEVEL_DOOR if is_progress_door(door_id) else Cell.OPTIONAL_DOOR
            )
            grid[ldy][ldx] = int(cell_type)
        return grid

    def get_nearby_powerup(self) -> str | None:
        """Devuelve el id del powerup adyacente (8 vecinos), o None."""
        bx, by = self.baby_pos
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                p = (bx + dx, by + dy)
                if p in self._remaining_powerups:
                    return self._remaining_powerups[p]
        return None

    def get_nearby_hazard(self) -> str | None:
        """Devuelve el id del hazard adyacente (8 vecinos), o None."""
        bx, by = self.baby_pos
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                p = (bx + dx, by + dy)
                if p in HAZARD_POSITIONS:
                    return HAZARD_POSITIONS[p]
        return None

    def get_nearby_special_door(self) -> str | None:
        """Devuelve el id de la puerta especial adyacente, o None."""
        bx, by = self.baby_pos
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                p = (bx + dx, by + dy)
                if p in SPECIAL_DOOR_POSITIONS:
                    return SPECIAL_DOOR_POSITIONS[p]
        return None

    # ── Internos ──────────────────────────────────────────────────────────────

    def _apply_action(self, action: int) -> list:
        x, y = self.baby_pos
        if action == 0:
            return [x, y - 1]
        elif action == 1:
            return [x, y + 1]
        elif action == 2:
            return [x - 1, y]
        elif action == 3:
            return [x + 1, y]
        else:
            return [x, y]

    def _cell_at(self, pos) -> Cell:
        pt = tuple(pos)
        if not (0 <= pos[0] < self.size and 0 <= pos[1] < self.size):
            return Cell.WALL
        if pt in self.walls:
            return Cell.WALL
        if pt == self.goal:
            return Cell.GOAL
        # 0.4.3: puertas de nivel tienen su propio tipo de celda
        door_id = LEVEL_DOOR_POSITIONS.get(pt)
        if door_id:
            return Cell.LEVEL_DOOR if is_progress_door(door_id) else Cell.OPTIONAL_DOOR
        return OBJECT_POSITIONS.get(pt, Cell.EMPTY)

    def _is_passable(self, pos, has_key: bool = False) -> bool:
        x, y = pos
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False
        if tuple(pos) in self.walls:
            return False
        cell = OBJECT_POSITIONS.get(tuple(pos), Cell.EMPTY)
        if cell == Cell.DOOR_CLOSED and not (has_key or self.door_open):
            return False
        return True

    def set_walls(self, walls: frozenset):
        """Actualiza las paredes del laberinto. Usado por level_factory en 0.2.1."""
        self.walls = walls

    def _is_valid(self, pos) -> bool:
        """Compatibilidad con tests 0.1.x (sin llave)."""
        return self._is_passable(pos)

    def _get_nearby_walls(self) -> list:
        x, y = self.baby_pos
        return [
            0.0 if self._is_passable([x, y - 1]) else 1.0,
            0.0 if self._is_passable([x, y + 1]) else 1.0,
            0.0 if self._is_passable([x - 1, y]) else 1.0,
            0.0 if self._is_passable([x + 1, y]) else 1.0,
        ]

    def _get_observation(self) -> np.ndarray:
        """Observacion base de 10 caracteristicas (sin inventario).
        El Trainer concatena 8 caracteristicas de inventario para llegar a 18."""
        bx, by = self.baby_pos
        gx, gy = self.goal
        walls = self._get_nearby_walls()
        n = float(self.size - 1)
        obs = [
            bx / n,
            by / n,
            (gx - bx) / n,
            (gy - by) / n,
            *walls,
            min(self.steps / MAX_STEPS, 1.0),
            min(len(self.visited) / (self.size * self.size), 1.0),
        ]
        return np.array(obs, dtype=np.float32)
