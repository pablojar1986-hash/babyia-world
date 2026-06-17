"""
brain/mission_reward.py — Reward shaping por mision para BabyIA World 0.4.4.

Entrega recompensas pequenas y no dominantes para guiar el aprendizaje.
No reemplaza REWARD_LEVEL_COMPLETED. El maximo acumulable por episodio
es mucho menor que completar el nivel (120 pts).
"""

from __future__ import annotations

from brain.mission import FIND_KEY, GO_TO_NEXT_LEVEL_DOOR

# ── Magnitudes de reward shaping ─────────────────────────────────────────────
# Todas inferiores a REWARD_LEVEL_COMPLETED (120) por varios ordenes de magnitud

APPROACH_KEY_BONUS = 0.3  # acercarse a llave cuando mision FIND_KEY
APPROACH_DOOR_BONUS = 0.3  # acercarse a puerta cuando GO_TO_NEXT_LEVEL_DOOR
MISSION_SWITCH_BONUS = 1.0  # cambio correcto FIND_KEY -> GO_TO_NEXT_LEVEL_DOOR
MOVE_AWAY_PENALTY = -0.2  # alejarse del objetivo principal
OPTIONAL_DISTRACTION_PENALTY = -0.3  # sala opcional sin llave (distraccion)


class MissionReward:
    """
    Calcula el reward shaping de mision por paso.
    prev_context y curr_context son dicts de DecisionContext.build().
    """

    def __init__(self):
        self.total_mission_reward: float = 0.0
        self.progress_steps: int = 0
        self.regression_steps: int = 0
        self.mission_switches: int = 0

    def reset_episode(self):
        self.total_mission_reward = 0.0
        self.progress_steps = 0
        self.regression_steps = 0
        self.mission_switches = 0

    def compute(
        self,
        prev_context: dict,
        curr_context: dict,
        info: dict,
    ) -> float:
        """Devuelve el delta de recompensa de mision para este paso."""
        delta = 0.0
        prev_goal = prev_context.get("current_goal", "")
        curr_goal = curr_context.get("current_goal", "")

        # 1. Acercarse a llave cuando FIND_KEY
        if curr_goal == FIND_KEY:
            prev_kd = prev_context.get("key_distance", 1.0)
            curr_kd = curr_context.get("key_distance", 1.0)
            if curr_kd < prev_kd - 0.01:
                delta += APPROACH_KEY_BONUS
                self.progress_steps += 1
            elif curr_kd > prev_kd + 0.05:
                delta += MOVE_AWAY_PENALTY
                self.regression_steps += 1

        # 2. Acercarse a puerta de progreso cuando GO_TO_NEXT_LEVEL_DOOR
        elif curr_goal == GO_TO_NEXT_LEVEL_DOOR:
            prev_pd = prev_context.get("progress_door_distance", 1.0)
            curr_pd = curr_context.get("progress_door_distance", 1.0)
            if curr_pd < prev_pd - 0.01:
                delta += APPROACH_DOOR_BONUS
                self.progress_steps += 1
            elif curr_pd > prev_pd + 0.05:
                delta += MOVE_AWAY_PENALTY
                self.regression_steps += 1

        # 3. Cambio de mision FIND_KEY -> GO_TO_NEXT_LEVEL_DOOR (recoge llave)
        if prev_goal == FIND_KEY and curr_goal == GO_TO_NEXT_LEVEL_DOOR:
            delta += MISSION_SWITCH_BONUS
            self.mission_switches += 1

        # 4. Penalizar distraccion en sala opcional cuando deberia buscar llave
        if info.get("entered_treasure_room") or info.get("entered_training_room"):
            if not curr_context.get("has_key", False):
                delta += OPTIONAL_DISTRACTION_PENALTY

        self.total_mission_reward += delta
        return delta

    def to_dict(self) -> dict:
        return {
            "total_mission_reward": round(self.total_mission_reward, 3),
            "progress_steps": self.progress_steps,
            "regression_steps": self.regression_steps,
            "mission_switches": self.mission_switches,
        }
