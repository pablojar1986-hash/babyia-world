"""
Definicion de peligros (hazards) en BabyIA World 0.4.
Cada peligro puede ser bloqueado por el estado corporal correcto.
Los peligros son mecanismos de juego, no amenazas reales.
"""

from dataclasses import dataclass


@dataclass
class HazardDef:
    hazard_id: str
    name: str
    effect: str  # nombre del efecto en BodyState.apply_hazard
    value: float  # magnitud del cambio
    blocked_by: str | None  # tipo de proteccion que bloquea este hazard
    danger_level: float  # 0.0 - 1.0
    description: str
    reward_delta: float  # penalizacion si no se bloquea

    def get_concept_signal(self) -> dict:
        return {
            "cause": self.hazard_id,
            "effect": self.effect,
            "countermeasure": self.blocked_by or "none",
            "danger_level": self.danger_level,
        }


HAZARD_TYPES: dict[str, HazardDef] = {
    "fire_zone": HazardDef(
        hazard_id="fire_zone",
        name="Zona de Fuego",
        effect="energy_damage",
        value=0.3,
        blocked_by="fire",
        danger_level=0.8,
        description="Dania a menos que tenga inmunidad al fuego.",
        reward_delta=-5.0,
    ),
    "poison_zone": HazardDef(
        hazard_id="poison_zone",
        name="Zona Venenosa",
        effect="energy_damage",
        value=0.25,
        blocked_by="poison",
        danger_level=0.7,
        description="Dania a menos que tenga inmunidad al veneno.",
        reward_delta=-4.0,
    ),
    "mud": HazardDef(
        hazard_id="mud",
        name="Lodo",
        effect="reduce_speed",
        value=0.3,
        blocked_by=None,
        danger_level=0.3,
        description="Reduce velocidad. No hay contrarrestante directo.",
        reward_delta=-1.5,
    ),
    "shrink_trap": HazardDef(
        hazard_id="shrink_trap",
        name="Trampa Encogedor",
        effect="reduce_size",
        value=0.3,
        blocked_by=None,
        danger_level=0.5,
        description="Reduce tamano. Puede impedir abrir puertas pesadas.",
        reward_delta=-2.0,
    ),
    "slow_trap": HazardDef(
        hazard_id="slow_trap",
        name="Trampa Ralentizadora",
        effect="reduce_speed",
        value=0.4,
        blocked_by=None,
        danger_level=0.4,
        description="Reduce velocidad significativamente.",
        reward_delta=-2.0,
    ),
    "darkness": HazardDef(
        hazard_id="darkness",
        name="Oscuridad",
        effect="reduce_vision",
        value=2.0,
        blocked_by=None,
        danger_level=0.4,
        description="Reduce rango de vision.",
        reward_delta=-1.5,
    ),
    "spikes": HazardDef(
        hazard_id="spikes",
        name="Espinas",
        effect="energy_damage",
        value=0.2,
        blocked_by="spikes",
        danger_level=0.6,
        description="Danian a menos que tenga escudo activo.",
        reward_delta=-3.0,
    ),
    "energy_drain": HazardDef(
        hazard_id="energy_drain",
        name="Drenador de Energia",
        effect="energy_damage",
        value=0.35,
        blocked_by=None,
        danger_level=0.7,
        description="Drena energia sin contrarrestante.",
        reward_delta=-4.0,
    ),
}


def is_blocked_by_body(hazard_id: str, body_state) -> bool:
    """Devuelve True si el estado corporal bloquea este peligro."""
    hz = HAZARD_TYPES.get(hazard_id)
    if not hz or not hz.blocked_by:
        return False
    return body_state.is_protected_against(hz.blocked_by)


def apply_hazard_to_body(hazard_id: str, body_state) -> tuple[float, bool]:
    """Aplica hazard. Devuelve (reward_delta, blocked)."""
    hz = HAZARD_TYPES.get(hazard_id)
    if not hz:
        return 0.0, False
    blocked = is_blocked_by_body(hazard_id, body_state)
    body_state.apply_hazard(hz.hazard_id, hz.effect, hz.value, blocked)
    reward = 0.0 if blocked else hz.reward_delta
    return reward, blocked
