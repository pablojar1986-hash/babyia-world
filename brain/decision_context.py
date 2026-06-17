"""
brain/decision_context.py — Contexto funcional de decision por paso (0.4.4).

Sintetiza el estado observable en un dict estructurado para UI, metricas
y reward shaping. No controla el DQN ni reemplaza las Q-values.
"""

from __future__ import annotations

from world.grid_world import HAZARD_POSITIONS

_MAX_DIST = 14.0  # distancia Manhattan maxima en grid 8x8
_PROGRESS_DOOR = (7, 7)
_KEY_POS = (1, 6)


class DecisionContext:
    """Construye un resumen funcional del estado actual por paso."""

    def build(
        self,
        world,
        inventory,
        body_state,
        world_manager,
        mission_state,
    ) -> dict:
        bx, by = world.baby_pos

        # Distancia a llave
        kx, ky = _KEY_POS
        key_dist = (
            (abs(bx - kx) + abs(by - ky)) / _MAX_DIST if world.key_present else 0.0
        )

        # Distancia a puerta de progreso
        px, py_ = _PROGRESS_DOOR
        prog_dist = (abs(bx - px) + abs(by - py_)) / _MAX_DIST

        # Amenaza mas cercana (radio 3)
        nearest_threat = None
        min_td = 999
        for (hx, hy), hid in HAZARD_POSITIONS.items():
            d = abs(bx - hx) + abs(by - hy)
            if d < min_td:
                min_td = d
                nearest_threat = hid if d <= 3 else None

        bs = body_state.to_dict() if hasattr(body_state, "to_dict") else {}
        has_shield = float(bs.get("shield", 0.0)) > 0.05

        # Puertas cercanas
        prog_nearby = world.get_nearby_progress_door()
        opt_door_id = world.get_nearby_level_door()
        opt_nearby = opt_door_id is not None and not prog_nearby

        should_ignore_optional = inventory.has_key or not world.key_present
        should_return_home = inventory.energy < 0.2 and not world_manager.is_at_home

        return {
            "has_key": inventory.has_key,
            "current_goal": mission_state.current_goal,
            "target_position": mission_state.target_position,
            "nearest_threat": nearest_threat,
            "nearest_useful_powerup": world.get_nearby_powerup(),
            "progress_door_distance": round(prog_dist, 3),
            "key_distance": round(key_dist, 3),
            "progress_door_nearby": prog_nearby,
            "optional_door_nearby": opt_nearby,
            "should_ignore_optional": should_ignore_optional,
            "should_return_home": should_return_home,
            "has_shield": has_shield,
            "energy": round(inventory.energy, 3),
        }
