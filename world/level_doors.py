"""
Puertas de nivel para BabyIA World 0.4.3.
Solo NEXT_LEVEL_DOOR completa el nivel; las demas son opcionales.
BabyIA aprende por experiencia cuál sirve para avanzar.
"""

from dataclasses import dataclass


@dataclass
class LevelDoor:
    door_id: str
    name: str
    door_type: str  # "next_level" | "treasure" | "danger_room" | "training_room"
    requires_key: bool = False
    reward_on_open: float = 0.0
    penalty_on_blocked: float = 0.0
    description: str = ""


LEVEL_DOOR_TYPES: dict[str, LevelDoor] = {
    "next_level_door": LevelDoor(
        door_id="next_level_door",
        name="Puerta de Siguiente Nivel",
        door_type="next_level",
        requires_key=True,
        reward_on_open=80.0,
        penalty_on_blocked=-5.0,
        description="Solo esta puerta completa el nivel. Requiere llave.",
    ),
    "treasure_door": LevelDoor(
        door_id="treasure_door",
        name="Puerta del Tesoro",
        door_type="treasure",
        requires_key=False,
        reward_on_open=10.0,
        penalty_on_blocked=0.0,
        description="Sala opcional con tesoro. No avanza de nivel.",
    ),
    "training_room_door": LevelDoor(
        door_id="training_room_door",
        name="Sala de Entrenamiento",
        door_type="training_room",
        requires_key=False,
        reward_on_open=5.0,
        penalty_on_blocked=0.0,
        description="Sala opcional con powerup. No avanza de nivel.",
    ),
}

# Posiciones fijas en el grid para nivel 0. Clave: (col, row).
# (7,7): puerta de progreso (donde antes estaba GOAL).
# (7,0): sala de entrenamiento (esquina superior derecha, libre).
# (4,7): sala del tesoro (borde inferior, libre).
LEVEL_DOOR_POSITIONS: dict[tuple, str] = {
    (7, 7): "next_level_door",
    (7, 0): "training_room_door",
    (4, 7): "treasure_door",
}


def is_progress_door(door_id: str) -> bool:
    """True si esta puerta es la de progreso de nivel."""
    door = LEVEL_DOOR_TYPES.get(door_id)
    return door is not None and door.door_type == "next_level"


def attempt_level_door(door_id: str, has_key: bool) -> dict:
    """
    Evalua si BabyIA puede cruzar esta puerta de nivel.
    Devuelve {can_pass, reward_delta, blocked_reason, level_completed}.
    """
    door = LEVEL_DOOR_TYPES.get(door_id)
    if not door:
        return {
            "can_pass": False,
            "reward_delta": 0.0,
            "blocked_reason": "puerta desconocida",
            "level_completed": False,
        }
    if door.requires_key and not has_key:
        return {
            "can_pass": False,
            "reward_delta": door.penalty_on_blocked,
            "blocked_reason": "necesita llave",
            "level_completed": False,
        }
    return {
        "can_pass": True,
        "reward_delta": door.reward_on_open,
        "blocked_reason": "",
        "level_completed": door.door_type == "next_level",
    }
