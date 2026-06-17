"""
brain/perception.py — Sistema de percepcion funcional para BabyIA 0.4.5.

BabyIA "ve" objetos cercanos dentro de un rango de vision.
"Ver" = detectar celdas dentro de rango Manhattan y clasificarlas.
No implica conciencia ni procesamiento subjetivo.
"""

from __future__ import annotations

from world.objects import Cell
from world.world_config import DEFAULT_VISION_RANGE

# Categorias semanticas de percepcion
CAT_GOAL = "goal"
CAT_DANGER = "danger"
CAT_REWARD = "reward"
CAT_OBSTACLE = "obstacle"
CAT_UNKNOWN = "unknown"
CAT_OPTIONAL = "optional"

_CELL_CATEGORY: dict[int, str] = {
    int(Cell.KEY): CAT_GOAL,
    int(Cell.LEVEL_DOOR): CAT_GOAL,
    int(Cell.DOOR_CLOSED): CAT_OBSTACLE,
    int(Cell.DOOR_OPEN): CAT_REWARD,
    int(Cell.FOOD): CAT_REWARD,
    int(Cell.POWERUP): CAT_REWARD,
    int(Cell.DANGER): CAT_DANGER,
    int(Cell.HAZARD): CAT_DANGER,
    int(Cell.WALL): CAT_OBSTACLE,
    int(Cell.OPTIONAL_DOOR): CAT_OPTIONAL,
    int(Cell.SPECIAL_DOOR): CAT_OPTIONAL,
    int(Cell.UNKNOWN_OBJECT): CAT_UNKNOWN,
    int(Cell.GOAL): CAT_GOAL,
    int(Cell.EMPTY): CAT_UNKNOWN,
}


class PerceptionSystem:
    """
    Detecta objetos cercanos en un rango de vision Manhattan.
    Devuelve un dict estructurado con objetos visibles clasificados.
    """

    def observe(
        self,
        world,
        baby_pos: tuple,
        vision_range: int = DEFAULT_VISION_RANGE,
        body_state=None,
    ) -> dict:
        bx, by = baby_pos
        gs = world.size
        grid = world.get_grid()

        visible_cells = []
        visible_objects = []
        nearest_key = None
        nearest_progress_door = None
        nearest_optional_door = None
        nearest_powerup = None
        nearest_hazard = None
        nearest_food = None
        nearest_wall = None

        min_key_d = 999
        min_door_d = 999
        min_opt_d = 999
        min_pu_d = 999
        min_hz_d = 999
        min_food_d = 999
        min_wall_d = 999

        danger_count = 0
        reward_count = 0
        unknown_count = 0

        for dx in range(-vision_range, vision_range + 1):
            for dy in range(-vision_range, vision_range + 1):
                if dx == 0 and dy == 0:
                    continue
                dist = abs(dx) + abs(dy)
                if dist > vision_range:
                    continue
                wx, wy = bx + dx, by + dy
                if not (0 <= wx < gs and 0 <= wy < gs):
                    continue

                cell_val = int(grid[wy][wx])
                cell_type = (
                    Cell(cell_val)
                    if cell_val in Cell._value2member_map_
                    else Cell.EMPTY
                )
                category = _CELL_CATEGORY.get(cell_val, CAT_UNKNOWN)
                pos = [wx, wy]

                cell_info = {
                    "position": pos,
                    "distance": dist,
                    "cell_type": cell_type.name,
                    "category": category,
                }
                visible_cells.append(cell_info)

                if cell_type == Cell.EMPTY:
                    continue

                # Contar por categoria
                if category == CAT_DANGER:
                    danger_count += 1
                elif category == CAT_REWARD:
                    reward_count += 1
                elif category == CAT_UNKNOWN:
                    unknown_count += 1

                obj_info = {
                    "kind": cell_type.name,
                    "position": pos,
                    "distance": dist,
                    "category": category,
                }
                visible_objects.append(obj_info)

                # Actualizar mas cercanos
                if cell_type == Cell.KEY and dist < min_key_d:
                    min_key_d = dist
                    nearest_key = obj_info
                elif cell_type == Cell.LEVEL_DOOR and dist < min_door_d:
                    min_door_d = dist
                    nearest_progress_door = obj_info
                elif cell_type == Cell.OPTIONAL_DOOR and dist < min_opt_d:
                    min_opt_d = dist
                    nearest_optional_door = obj_info
                elif cell_type == Cell.POWERUP and dist < min_pu_d:
                    min_pu_d = dist
                    nearest_powerup = obj_info
                elif cell_type in (Cell.HAZARD, Cell.DANGER) and dist < min_hz_d:
                    min_hz_d = dist
                    nearest_hazard = obj_info
                elif cell_type == Cell.FOOD and dist < min_food_d:
                    min_food_d = dist
                    nearest_food = obj_info
                elif cell_type == Cell.WALL and dist < min_wall_d:
                    min_wall_d = dist
                    nearest_wall = obj_info

        return {
            "vision_range": vision_range,
            "visible_cells": visible_cells,
            "visible_objects": visible_objects,
            "nearest_key": nearest_key,
            "nearest_progress_door": nearest_progress_door,
            "nearest_optional_door": nearest_optional_door,
            "nearest_powerup": nearest_powerup,
            "nearest_hazard": nearest_hazard,
            "nearest_food": nearest_food,
            "nearest_wall": nearest_wall,
            "danger_count": danger_count,
            "reward_count": reward_count,
            "unknown_count": unknown_count,
            "total_visible": len(visible_objects),
        }
