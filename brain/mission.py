"""
brain/mission.py — Sistema de mision funcional para BabyIA World 0.4.4.

Calcula el objetivo actual a partir del estado del episodio.
Esto es calculo de prioridad basado en recompensa y riesgo, no conciencia real.
BabyIA no "quiere" misiones; el sistema calcula la que maximiza progreso esperado.
"""

from __future__ import annotations

from dataclasses import dataclass

# ── Constantes de estado de mision ──────────────────────────────────────────

FIND_KEY = "FIND_KEY"
GO_TO_NEXT_LEVEL_DOOR = "GO_TO_NEXT_LEVEL_DOOR"
EXPLORE_OPTIONAL_ROOM = "EXPLORE_OPTIONAL_ROOM"
AVOID_DANGER = "AVOID_DANGER"
COLLECT_USEFUL_POWERUP = "COLLECT_USEFUL_POWERUP"
RETURN_HOME = "RETURN_HOME"
LEVEL_COMPLETED = "LEVEL_COMPLETED"

# Posiciones por defecto (8x8) — MissionTracker usa posiciones dinamicas del world
KEY_POS = (1, 6)
PROGRESS_DOOR_POS = (7, 7)

LOW_ENERGY_THRESHOLD = 0.25


@dataclass
class MissionState:
    """Estado de mision actual — calculado funcionalmente, no elegido conscientemente."""

    current_goal: str = FIND_KEY
    target_position: tuple | None = None
    priority: float = 1.0
    reason: str = ""
    progress_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "current_goal": self.current_goal,
            "target_position": (
                list(self.target_position) if self.target_position else None
            ),
            "priority": round(self.priority, 3),
            "reason": self.reason,
            "progress_score": round(self.progress_score, 3),
        }


class MissionTracker:
    """
    Calcula la mision actual a partir del contexto de episodio.
    No controla el DQN. Produce datos para reward shaping, UI y metricas.
    """

    def compute(
        self,
        has_key: bool,
        level_completed: bool,
        energy: float,
        danger_nearby: bool,
        has_shield: bool,
        is_at_home: bool,
        step_count: int,
        baby_pos: tuple,
        key_present: bool,
        key_pos: tuple = KEY_POS,
        progress_door_pos: tuple = PROGRESS_DOOR_POS,
    ) -> MissionState:
        bx, by = baby_pos
        gs = max(key_pos[0], key_pos[1], progress_door_pos[0], progress_door_pos[1]) + 1
        _max_dist = (gs - 1) * 2.0

        # 1. Nivel completado (terminal)
        if level_completed:
            return MissionState(
                current_goal=LEVEL_COMPLETED,
                target_position=progress_door_pos,
                priority=1.0,
                reason="Puerta dorada cruzada con llave",
                progress_score=1.0,
            )

        # 2. Peligro cercano sin proteccion (temporal, alta prioridad)
        if danger_nearby and not has_shield and energy < LOW_ENERGY_THRESHOLD:
            return MissionState(
                current_goal=AVOID_DANGER,
                target_position=None,
                priority=0.9,
                reason="Peligro cercano con energia baja y sin escudo",
                progress_score=0.0,
            )

        # 3. Tiene llave -> ir a puerta de progreso
        if has_key:
            px, py_ = progress_door_pos
            dist = abs(bx - px) + abs(by - py_)
            progress = max(0.0, 1.0 - dist / _max_dist)
            return MissionState(
                current_goal=GO_TO_NEXT_LEVEL_DOOR,
                target_position=progress_door_pos,
                priority=1.0,
                reason=f"Llave recogida. Ir a puerta dorada {progress_door_pos}",
                progress_score=progress,
            )

        # 4. Sin llave -> buscarla
        kx, ky = key_pos
        dist_key = abs(bx - kx) + abs(by - ky)
        progress = max(0.0, 1.0 - dist_key / _max_dist) if key_present else 0.5
        reason = (
            "La puerta dorada requiere llave"
            if key_present
            else "Llave recogida antes en el episodio"
        )
        return MissionState(
            current_goal=FIND_KEY,
            target_position=key_pos if key_present else None,
            priority=0.95,
            reason=reason,
            progress_score=progress,
        )
