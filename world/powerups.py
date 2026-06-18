"""
Definicion de powerups (recompensas evolutivas) disponibles en BabyIA World 0.4.
Cada powerup modifica atributos del BodyState y genera una senal causal.
Los powerups son mecanismos de juego, no habilidades reales.
"""

from dataclasses import dataclass


@dataclass
class PowerupDef:
    powerup_id: str
    name: str
    effect: str  # nombre del efecto en BodyState.apply_powerup
    value: float  # magnitud del cambio
    duration: int  # 0 = permanente en el episodio
    description: str
    reward_delta: float  # recompensa inmediata al recogerlo

    def get_concept_signal(self) -> dict:
        return {
            "cause": self.powerup_id,
            "effect": self.effect,
            "useful_for": _USEFUL_FOR.get(self.powerup_id, "unknown"),
        }


_USEFUL_FOR = {
    "growth_crystal": "heavy_door",
    "speed_boots": "speed_door",
    "shield_orb": "spikes",
    "fire_immunity": "fire_door",
    "poison_immunity": "poison_door",
    "vision_light": "dark_zone",
    "memory_crystal": "memory_door",
    "energy_food": "low_energy",
}

POWERUP_TYPES: dict[str, PowerupDef] = {
    "growth_crystal": PowerupDef(
        powerup_id="growth_crystal",
        name="Cristal de Crecimiento",
        effect="increase_size",
        value=0.5,
        duration=0,
        description="Aumenta el tamano de BabyIA permanentemente en el episodio.",
        reward_delta=3.0,
    ),
    "speed_boots": PowerupDef(
        powerup_id="speed_boots",
        name="Botas de Velocidad",
        effect="increase_speed",
        value=0.5,
        duration=50,
        description="Aumenta la velocidad temporalmente.",
        reward_delta=2.0,
    ),
    "shield_orb": PowerupDef(
        powerup_id="shield_orb",
        name="Orbe de Escudo",
        effect="add_shield",
        value=0.5,
        duration=0,
        description="Agrega escudo protector temporal.",
        reward_delta=2.5,
    ),
    "fire_immunity": PowerupDef(
        powerup_id="fire_immunity",
        name="Amuleto de Fuego",
        effect="fire_immunity",
        value=1.0,
        duration=0,
        description="Inmunidad al fuego en este episodio.",
        reward_delta=4.0,
    ),
    "poison_immunity": PowerupDef(
        powerup_id="poison_immunity",
        name="Antivenenoso",
        effect="poison_immunity",
        value=1.0,
        duration=0,
        description="Inmunidad al veneno en este episodio.",
        reward_delta=4.0,
    ),
    "vision_light": PowerupDef(
        powerup_id="vision_light",
        name="Luz de Vision",
        effect="increase_vision",
        value=2.0,
        duration=80,
        description="Aumenta el rango de vision.",
        reward_delta=2.0,
    ),
    "memory_crystal": PowerupDef(
        powerup_id="memory_crystal",
        name="Cristal de Memoria",
        effect="increase_memory_focus",
        value=0.3,
        duration=0,
        description="Aumenta la confianza de la memoria causal.",
        reward_delta=2.0,
    ),
    "energy_food": PowerupDef(
        powerup_id="energy_food",
        name="Comida Energetica",
        effect="energy_restore",
        value=0.5,
        duration=0,
        description="Restaura energia de forma acelerada.",
        reward_delta=3.0,
    ),
}


def apply_powerup_to_body(powerup_id: str, body_state) -> float:
    """Aplica powerup al BodyState. Devuelve reward_delta."""
    pu = POWERUP_TYPES.get(powerup_id)
    if not pu:
        return 0.0
    body_state.apply_powerup(pu.powerup_id, pu.effect, pu.value, pu.duration)
    return pu.reward_delta


def apply_powerup_effect(powerup_id: str, body_state, inventory) -> float:
    """
    Aplica el efecto completo de un powerup a BodyState e Inventory.
    energy_restore afecta inventory.energy; el resto afectan body_state.
    Devuelve reward_delta.
    """
    pu = POWERUP_TYPES.get(powerup_id)
    if not pu:
        return 0.0
    if pu.effect == "energy_restore":
        inventory.restore_energy(pu.value)
    else:
        body_state.apply_powerup(pu.powerup_id, pu.effect, pu.value, pu.duration)
    return pu.reward_delta
