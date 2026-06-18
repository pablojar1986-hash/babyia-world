"""Portal: puerta que conecta dos mundos. Tiene posicion en el grid 8x8."""

from dataclasses import dataclass


@dataclass
class Portal:
    portal_id: str
    target_world: str  # world_id del mundo destino
    label: str
    required_level: int  # nivel minimo para poder entrar
    position: tuple  # (x, y) en el grid 8x8
    color: tuple  # RGB para el renderizador
    is_unlocked: bool = True

    def can_enter(self, player_level: int) -> bool:
        return self.is_unlocked and player_level >= self.required_level

    def to_dict(self) -> dict:
        return {
            "portal_id": self.portal_id,
            "target_world": self.target_world,
            "label": self.label,
            "required_level": self.required_level,
            "position": list(self.position),
            "color": list(self.color),
            "is_unlocked": self.is_unlocked,
        }
