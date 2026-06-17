"""
Estado corporal de BabyIA: atributos fisicos simulados.
Estos son mecanismos de juego, no indicadores biologicos reales.
Persiste dentro del episodio; se reinicia al comenzar uno nuevo.
"""
import numpy as np

MAX_SIZE  = 3.0
MAX_SPEED = 3.0
MIN_SIZE  = 0.5
MIN_SPEED = 0.5
SHIELD_DECAY = 0.02   # escudo se reduce por paso


class BodyState:
    def __init__(self):
        self.size            : float = 1.0
        self.speed           : float = 1.0
        self.shield          : float = 0.0   # 0-1, proteccion temporal
        self.fire_immunity   : bool  = False
        self.poison_immunity : bool  = False
        self.vision_range    : int   = 3
        self.memory_focus    : float = 1.0
        self._effects        : list[dict] = []  # efectos temporales activos

    # ── Aplicar cambios ───────────────────────────────────────────────────────

    def apply_powerup(self, powerup_id: str, effect: str, value: float,
                      duration: int = 0):
        """Aplica un powerup al estado corporal."""
        if effect == "increase_size":
            self.size = min(MAX_SIZE, self.size + value)
        elif effect == "increase_speed":
            self.speed = min(MAX_SPEED, self.speed + value)
        elif effect == "add_shield":
            self.shield = min(1.0, self.shield + value)
        elif effect == "fire_immunity":
            self.fire_immunity = True
        elif effect == "poison_immunity":
            self.poison_immunity = True
        elif effect == "increase_vision":
            self.vision_range = min(7, self.vision_range + int(value))
        elif effect == "increase_memory_focus":
            self.memory_focus = min(2.0, self.memory_focus + value)

        if duration > 0:
            self._effects.append({
                "powerup_id": powerup_id, "effect": effect,
                "value": value, "remaining": duration,
            })

    def apply_hazard(self, hazard_id: str, effect: str, value: float,
                     blocked: bool = False) -> float:
        """
        Aplica un hazard al estado corporal.
        Devuelve danio de energia causado (0 si bloqueado).
        """
        if blocked:
            return 0.0
        if effect == "reduce_speed":
            self.speed = max(MIN_SPEED, self.speed - value)
        elif effect == "reduce_size":
            self.size = max(MIN_SIZE, self.size - value)
        elif effect == "reduce_shield":
            self.shield = max(0.0, self.shield - value)
        elif effect == "reduce_vision":
            self.vision_range = max(1, self.vision_range - int(value))
        elif effect == "energy_damage":
            return value   # el trainer lo aplica sobre Inventory
        return 0.0

    # ── Tick por paso ─────────────────────────────────────────────────────────

    def tick_effects(self):
        """Decrementa duracion de efectos activos; revierte los expirados."""
        active = []
        for eff in self._effects:
            eff["remaining"] -= 1
            if eff["remaining"] > 0:
                active.append(eff)
            else:
                self._revert_effect(eff)
        self._effects = active
        # Escudo se degrada pasivamente
        if self.shield > 0:
            self.shield = max(0.0, self.shield - SHIELD_DECAY)

    # ── Episodio ──────────────────────────────────────────────────────────────

    def reset_for_episode(self):
        self.size            = 1.0
        self.speed           = 1.0
        self.shield          = 0.0
        self.fire_immunity   = False
        self.poison_immunity = False
        self.vision_range    = 3
        self.memory_focus    = 1.0
        self._effects        = []

    # ── Estado para DQN ───────────────────────────────────────────────────────

    def get_state_features(self) -> np.ndarray:
        """
        8 features del estado corporal para el vector de observacion.
        Indices 26-33 del STATE_SIZE=34.
        Features 31-33 reservadas para proximidad (siempre 0.0 en 0.4.0).
        """
        return np.array([
            self.size  / MAX_SIZE,
            self.speed / MAX_SPEED,
            min(self.shield, 1.0),
            float(self.fire_immunity),
            float(self.poison_immunity),
            0.0,   # powerup_nearby  (0.4.1+)
            0.0,   # hazard_nearby   (0.4.1+)
            0.0,   # door_req_nearby (0.4.2+)
        ], dtype=np.float32)

    # ── Consultas ─────────────────────────────────────────────────────────────

    def is_protected_against(self, hazard_type: str) -> bool:
        if hazard_type == "fire" and self.fire_immunity:
            return True
        if hazard_type == "poison" and self.poison_immunity:
            return True
        if hazard_type == "spikes" and self.shield > 0:
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "size"           : round(self.size, 2),
            "speed"          : round(self.speed, 2),
            "shield"         : round(self.shield, 2),
            "fire_immunity"  : self.fire_immunity,
            "poison_immunity": self.poison_immunity,
            "vision_range"   : self.vision_range,
            "memory_focus"   : round(self.memory_focus, 2),
            "active_effects" : len(self._effects),
        }

    # ── Internos ──────────────────────────────────────────────────────────────

    def _revert_effect(self, eff: dict):
        effect, value = eff["effect"], eff["value"]
        if effect == "increase_size":
            self.size = max(MIN_SIZE, self.size - value)
        elif effect == "increase_speed":
            self.speed = max(MIN_SPEED, self.speed - value)
        elif effect == "fire_immunity":
            self.fire_immunity = False
        elif effect == "poison_immunity":
            self.poison_immunity = False
