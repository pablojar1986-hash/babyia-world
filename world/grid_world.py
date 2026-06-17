import numpy as np
from world.objects import Cell
from world.rewards import calculate_reward
from world.level_doors import (
    LEVEL_DOOR_POSITIONS,
    LEVEL_DOOR_TYPES,
    attempt_level_door,
    is_progress_door,
)
from world.world_config import (
    DEFAULT_GRID_SIZE,
    get_key_pos,
    get_door_pos,
    get_food_pos,
    get_danger_pos,
    get_unknown_pos,
    get_progress_door_pos,
    get_training_door_pos,
    get_treasure_door_pos,
    get_powerup_positions,
    get_hazard_positions,
    get_special_door_positions,
    get_start_pos,
)

# Modulo-level constants: compatibilidad con tests existentes (grid 8x8)
WALL_POSITIONS = frozenset(
    {
        (2, 0),
        (2, 1),
        (2, 2),
        (2, 3),
        (5, 4),
        (5, 5),
        (5, 6),
        (5, 7),
        (4, 2),
        (3, 4),
    }
)

OBJECT_POSITIONS: dict[tuple, Cell] = {
    (1, 6): Cell.KEY,
    (3, 6): Cell.DOOR_CLOSED,
    (6, 2): Cell.FOOD,
    (3, 5): Cell.DANGER,
    (7, 1): Cell.UNKNOWN_OBJECT,
}

POWERUP_POSITIONS: dict[tuple, str] = {
    (0, 3): "growth_crystal",
    (4, 0): "shield_orb",
    (6, 5): "energy_food",
    (1, 5): "speed_boots",
}

HAZARD_POSITIONS: dict[tuple, str] = {
    (1, 2): "fire_zone",
    (0, 6): "spikes",
    (6, 3): "mud",
}

SPECIAL_DOOR_POSITIONS: dict[tuple, str] = {
    (3, 0): "heavy_door",
    (5, 2): "small_door",
}

GOAL_POS = (7, 7)
START_POS = (0, 0)
MAX_STEPS = 200

_BASE_OBS = 10


class GridWorld:
    def __init__(self, grid_size: int = DEFAULT_GRID_SIZE):
        gs = grid_size

        # Posiciones dinamicas derivadas del tamano del grid
        self.key_pos: tuple = get_key_pos(gs)
        self.door_pos: tuple = get_door_pos(gs)
        self.food_pos: tuple = get_food_pos(gs)
        self.danger_pos: tuple = get_danger_pos(gs)
        self.unknown_pos: tuple = get_unknown_pos(gs)
        self.progress_door_pos: tuple = get_progress_door_pos(gs)
        self.start_pos: tuple = get_start_pos(gs)

        # Para compatibilidad con codigo que usa world.goal
        self.goal = self.progress_door_pos

        self.size: int = gs
        self.walls: frozenset = (
            WALL_POSITIONS if gs == DEFAULT_GRID_SIZE else frozenset()
        )

        # Objetos interactivos dinamicos
        self._base_object_positions: dict[tuple, Cell] = {
            self.key_pos: Cell.KEY,
            self.door_pos: Cell.DOOR_CLOSED,
            self.food_pos: Cell.FOOD,
            self.danger_pos: Cell.DANGER,
            self.unknown_pos: Cell.UNKNOWN_OBJECT,
        }

        # Posiciones de powerups/hazards/puertas especiales dinamicas
        self._base_powerup_positions: dict[tuple, str] = get_powerup_positions(gs)
        self._hazard_positions: dict[tuple, str] = get_hazard_positions(gs)
        self._special_door_positions: dict[tuple, str] = get_special_door_positions(gs)

        # Puertas de nivel dinamicas
        self._level_door_positions: dict[tuple, str] = (
            LEVEL_DOOR_POSITIONS
            if gs == DEFAULT_GRID_SIZE
            else {
                get_progress_door_pos(gs): "next_level_door",
                get_training_door_pos(gs): "training_room_door",
                get_treasure_door_pos(gs): "treasure_door",
            }
        )

        self.reset()

    # ── Control de episodio ────────────────────────────────────────────────────

    def reset(self) -> np.ndarray:
        self.baby_pos = list(self.start_pos)
        self.steps = 0
        self.visited = {self.start_pos}
        self.action_history: list[int] = []
        self.last_reward = 0.0
        self.hit_wall = False
        self.done = False
        self.key_present = True
        self.door_open = False
        self.food_present = True
        self.unknown_touched = False
        self._remaining_powerups: dict[tuple, str] = dict(self._base_powerup_positions)
        return self._get_observation()

    # ── Paso de simulacion ────────────────────────────────────────────────────

    def step(self, action: int, has_key: bool = False):
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

        level_door_id = self._level_door_positions.get(pos_t)
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

            pu = self._remaining_powerups.get(pos_t)
            if pu:
                del self._remaining_powerups[pos_t]
                info_obj["hit_powerup"] = pu
            hz = self._hazard_positions.get(pos_t)
            if hz:
                info_obj["hit_hazard"] = hz
            sd = self._special_door_positions.get(pos_t)
            if sd:
                info_obj["hit_special_door"] = sd

            if level_door_id:
                result = attempt_level_door(level_door_id, has_key)
                door_def = LEVEL_DOOR_TYPES[level_door_id]
                if result["level_completed"]:
                    info_obj["level_completed"] = True
                    info_obj["next_level_door_opened"] = True
                    reached_goal = True
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
            if next_level_blocked:
                info_obj["hit_next_level_door"] = True
                info_obj["missing_requirement"] = "necesita llave"
                hit_wall = False

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
        return {
            "key_pos": self.key_pos,
            "key_present": self.key_present,
            "door_pos": self.door_pos,
            "door_open": self.door_open,
            "food_pos": self.food_pos,
            "food_present": self.food_present,
            "danger_pos": self.danger_pos,
            "unknown_pos": self.unknown_pos,
        }

    def danger_nearby(self) -> bool:
        bx, by = self.baby_pos
        dx, dy = self.danger_pos
        return abs(bx - dx) + abs(by - dy) <= 1

    def get_nearby_level_door(self) -> str | None:
        bx, by = self.baby_pos
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                p = (bx + ddx, by + ddy)
                if p in self._level_door_positions:
                    return self._level_door_positions[p]
        return None

    def get_nearby_progress_door(self) -> bool:
        bx, by = self.baby_pos
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                p = (bx + ddx, by + ddy)
                door_id = self._level_door_positions.get(p)
                if door_id and is_progress_door(door_id):
                    return True
        return False

    def get_grid(self) -> np.ndarray:
        gs = self.size
        grid = np.zeros((gs, gs), dtype=int)
        for wx, wy in self.walls:
            if 0 <= wy < gs and 0 <= wx < gs:
                grid[wy][wx] = int(Cell.WALL)

        # Objetos dinamicos basicos
        kx, ky = self.key_pos
        if self.key_present:
            grid[ky][kx] = int(Cell.KEY)

        dx_d, dy_d = self.door_pos
        door_state = Cell.DOOR_OPEN if self.door_open else Cell.DOOR_CLOSED
        grid[dy_d][dx_d] = int(door_state)

        fx, fy = self.food_pos
        if self.food_present:
            grid[fy][fx] = int(Cell.FOOD)

        dgx, dgy = self.danger_pos
        grid[dgy][dgx] = int(Cell.DANGER)

        ux, uy = self.unknown_pos
        grid[uy][ux] = int(Cell.UNKNOWN_OBJECT)

        # Powerups restantes, hazards, puertas especiales
        for (px, py), _ in self._remaining_powerups.items():
            if 0 <= py < gs and 0 <= px < gs:
                grid[py][px] = int(Cell.POWERUP)
        for hx, hy in self._hazard_positions:
            if 0 <= hy < gs and 0 <= hx < gs:
                grid[hy][hx] = int(Cell.HAZARD)
        for sdx, sdy in self._special_door_positions:
            if 0 <= sdy < gs and 0 <= sdx < gs:
                grid[sdy][sdx] = int(Cell.SPECIAL_DOOR)

        # Puertas de nivel (sobreescriben todo)
        for (ldx, ldy), door_id in self._level_door_positions.items():
            if 0 <= ldy < gs and 0 <= ldx < gs:
                cell_type = (
                    Cell.LEVEL_DOOR if is_progress_door(door_id) else Cell.OPTIONAL_DOOR
                )
                grid[ldy][ldx] = int(cell_type)

        return grid

    def get_nearby_powerup(self) -> str | None:
        bx, by = self.baby_pos
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                p = (bx + ddx, by + ddy)
                if p in self._remaining_powerups:
                    return self._remaining_powerups[p]
        return None

    def get_nearby_hazard(self) -> str | None:
        bx, by = self.baby_pos
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                p = (bx + ddx, by + ddy)
                if p in self._hazard_positions:
                    return self._hazard_positions[p]
        return None

    def get_nearby_special_door(self) -> str | None:
        bx, by = self.baby_pos
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                p = (bx + ddx, by + ddy)
                if p in self._special_door_positions:
                    return self._special_door_positions[p]
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
        if pt == self.progress_door_pos:
            return Cell.LEVEL_DOOR
        door_id = self._level_door_positions.get(pt)
        if door_id:
            return Cell.LEVEL_DOOR if is_progress_door(door_id) else Cell.OPTIONAL_DOOR
        return self._base_object_positions.get(pt, Cell.EMPTY)

    def _is_passable(self, pos, has_key: bool = False) -> bool:
        x, y = pos
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False
        if tuple(pos) in self.walls:
            return False
        cell = self._base_object_positions.get(tuple(pos), Cell.EMPTY)
        if cell == Cell.DOOR_CLOSED and not (has_key or self.door_open):
            return False
        return True

    def set_walls(self, walls: frozenset):
        self.walls = walls

    def _is_valid(self, pos) -> bool:
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
        bx, by = self.baby_pos
        gx, gy = self.progress_door_pos
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
