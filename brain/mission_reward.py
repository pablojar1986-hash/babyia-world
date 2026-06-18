"""
brain/mission_reward.py — Reward shaping por mision para BabyIA World 0.4.4.

Entrega recompensas pequenas y no dominantes para guiar el aprendizaje.
No reemplaza REWARD_LEVEL_COMPLETED. El maximo acumulable positivo por episodio
esta limitado por MAX_MISSION_REWARD_PER_EPISODE.

0.4.6b: cap de recompensa por episodio, penalizacion de oscilacion, choques y hazards repetidos.
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

# 0.4.6b: anti-estancamiento
MAX_MISSION_REWARD_PER_EPISODE = 8.0  # techo de reward positivo por episodio
WALL_REPEAT_PENALTY = -0.1  # choque repetido contra misma posicion
HAZARD_REPEAT_PENALTY = -0.15  # entrada repetida al mismo hazard
OSCILLATION_PENALTY = -0.1  # oscilacion entre las mismas celdas
_RECENT_POS_WINDOW = 10  # ventana de posiciones recientes para detectar oscilacion
_OSCILLATION_THRESHOLD = (
    3  # veces que una posicion debe aparecer para considerar oscilacion
)


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
        self.oscillation_steps: int = 0
        self._recent_positions: list[tuple] = []

    def reset_episode(self):
        self.total_mission_reward = 0.0
        self.progress_steps = 0
        self.regression_steps = 0
        self.mission_switches = 0
        self.oscillation_steps = 0
        self._recent_positions = []

    def compute(
        self,
        prev_context: dict,
        curr_context: dict,
        info: dict,
        baby_pos: tuple | None = None,
        visual_memory_stats: dict | None = None,
    ) -> float:
        """Devuelve el delta de recompensa de mision para este paso."""
        delta = 0.0
        prev_goal = prev_context.get("current_goal", "")
        curr_goal = curr_context.get("current_goal", "")

        # 1. Acercarse a llave cuando FIND_KEY (solo si no se ha alcanzado el cap positivo)
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

        # ── 0.4.6b: penalizaciones de anti-estancamiento ──────────────────────

        # 5. Choque repetido contra la misma pared
        if info.get("repeated_wall"):
            delta += WALL_REPEAT_PENALTY

        # 6. Entrada repetida al mismo hazard
        if info.get("repeated_hazard"):
            delta += HAZARD_REPEAT_PENALTY

        # 7. Oscilacion entre las mismas celdas (detectada por ventana de posiciones)
        if baby_pos is not None:
            self._recent_positions.append(baby_pos)
            if len(self._recent_positions) > _RECENT_POS_WINDOW:
                self._recent_positions.pop(0)
            if self._recent_positions.count(baby_pos) >= _OSCILLATION_THRESHOLD:
                delta += OSCILLATION_PENALTY
                self.oscillation_steps += 1

        # ── Cap de recompensa positiva por episodio ───────────────────────────
        if delta > 0 and self.total_mission_reward >= MAX_MISSION_REWARD_PER_EPISODE:
            delta = 0.0

        self.total_mission_reward += delta
        return delta

    def to_dict(self) -> dict:
        return {
            "total_mission_reward": round(self.total_mission_reward, 3),
            "progress_steps": self.progress_steps,
            "regression_steps": self.regression_steps,
            "mission_switches": self.mission_switches,
            "oscillation_steps": self.oscillation_steps,
        }
