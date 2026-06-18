"""
Puertas con requisitos especiales en BabyIA World 0.4.
Cada tipo de puerta requiere un atributo corporal o powerup especifico.
BabyIA aprende por ensayo-error que necesita para abrir cada tipo.
"""

from dataclasses import dataclass


@dataclass
class DoorRequirement:
    door_id: str
    name: str
    required_size: float = 1.0
    required_speed: float = 1.0
    required_powerup: str | None = None
    required_concept: str | None = None
    max_size: float = 999.0  # 0.4.2: limite superior de tamano (small_door)
    reward_on_open: float = 5.0
    penalty_on_fail: float = -1.0
    description: str = ""

    def can_pass(self, body_state, known_concepts: set | None = None) -> bool:
        """True si el estado corporal cumple todos los requisitos."""
        if body_state.size < self.required_size:
            return False
        if body_state.size > self.max_size:
            return False
        if body_state.speed < self.required_speed:
            return False
        if self.required_powerup == "fire_immunity" and not body_state.fire_immunity:
            return False
        if (
            self.required_powerup == "poison_immunity"
            and not body_state.poison_immunity
        ):
            return False
        if self.required_concept and known_concepts:
            if self.required_concept not in known_concepts:
                return False
        return True

    def get_fail_reason(self, body_state) -> str:
        if body_state.size < self.required_size:
            return f"tamano insuficiente ({body_state.size:.1f} < {self.required_size})"
        if body_state.size > self.max_size:
            return f"tamano excesivo ({body_state.size:.1f} > {self.max_size})"
        if body_state.speed < self.required_speed:
            return f"velocidad insuficiente ({body_state.speed:.1f} < {self.required_speed})"
        if self.required_powerup == "fire_immunity" and not body_state.fire_immunity:
            return "necesita inmunidad al fuego"
        if (
            self.required_powerup == "poison_immunity"
            and not body_state.poison_immunity
        ):
            return "necesita inmunidad al veneno"
        return "requisito no cumplido"

    def to_dict(self) -> dict:
        return {
            "door_id": self.door_id,
            "name": self.name,
            "required_size": self.required_size,
            "required_speed": self.required_speed,
            "required_powerup": self.required_powerup,
            "required_concept": self.required_concept,
        }


DOOR_TYPES: dict[str, DoorRequirement] = {
    "heavy_door": DoorRequirement(
        door_id="heavy_door",
        name="Puerta Pesada",
        required_size=1.5,
        description="Requiere tamano mayor o igual a 1.5.",
        reward_on_open=8.0,
    ),
    "speed_door": DoorRequirement(
        door_id="speed_door",
        name="Puerta Rapida",
        required_speed=1.5,
        description="Requiere velocidad mayor o igual a 1.5.",
        reward_on_open=8.0,
    ),
    "fire_door": DoorRequirement(
        door_id="fire_door",
        name="Puerta de Fuego",
        required_powerup="fire_immunity",
        description="Requiere inmunidad al fuego.",
        reward_on_open=10.0,
    ),
    "poison_door": DoorRequirement(
        door_id="poison_door",
        name="Puerta Venenosa",
        required_powerup="poison_immunity",
        description="Requiere inmunidad al veneno.",
        reward_on_open=10.0,
    ),
    "small_door": DoorRequirement(
        door_id="small_door",
        name="Puerta Pequena",
        required_size=0.0,
        max_size=1.2,  # 0.4.2: solo pasa si size <= 1.2
        description="Solo cabe BabyIA si no es demasiado grande (size <= 1.2).",
        reward_on_open=6.0,
    ),
    "memory_door": DoorRequirement(
        door_id="memory_door",
        name="Puerta de Memoria",
        required_concept="key_opens_door",
        description="Requiere que BabyIA haya aprendido el concepto llave-abre-puerta.",
        reward_on_open=12.0,
    ),
}


def attempt_door(door_id: str, body_state, known_concepts: set | None = None) -> dict:
    """
    Intenta abrir una puerta. Devuelve {success, reward_delta, fail_reason}.
    """
    door = DOOR_TYPES.get(door_id)
    if not door:
        return {
            "success": False,
            "reward_delta": 0.0,
            "fail_reason": "puerta desconocida",
        }
    success = door.can_pass(body_state, known_concepts)
    return {
        "success": success,
        "reward_delta": door.reward_on_open if success else door.penalty_on_fail,
        "fail_reason": "" if success else door.get_fail_reason(body_state),
    }
