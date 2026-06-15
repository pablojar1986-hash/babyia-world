"""Definicion de un mundo: sus propiedades y condiciones de acceso."""
from dataclasses import dataclass


@dataclass
class WorldDefinition:
    world_id: str
    name: str
    reward_profile: str  # clave en REWARD_PROFILES
    risk_level: float    # 0.0 (seguro) a 1.0 (muy peligroso)
    complexity: int      # 1-5
    home_return_required: bool
    min_level: int       # nivel minimo de BabyIA para poder entrar
    description: str

    def is_accessible(self, player_level: int) -> bool:
        return player_level >= self.min_level

    def to_dict(self) -> dict:
        return {
            "world_id"            : self.world_id,
            "name"                : self.name,
            "reward_profile"      : self.reward_profile,
            "risk_level"          : self.risk_level,
            "complexity"          : self.complexity,
            "home_return_required": self.home_return_required,
            "min_level"           : self.min_level,
            "description"         : self.description,
        }
