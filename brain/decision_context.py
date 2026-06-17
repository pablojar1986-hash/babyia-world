"""
brain/decision_context.py — Contexto funcional de decision por paso (0.4.5b).

Sintetiza el estado observable en un dict estructurado para UI, metricas
y reward shaping. Incluye datos de percepcion y memoria visual.
No controla el DQN ni reemplaza las Q-values.
"""

from __future__ import annotations

# Fallbacks para compatibilidad con mocks en tests
_KEY_POS_DEFAULT = (1, 6)
_PROGRESS_DOOR_DEFAULT = (7, 7)


class DecisionContext:
    """Construye un resumen funcional del estado actual por paso."""

    def build(
        self,
        world,
        inventory,
        body_state,
        world_manager,
        mission_state,
        perception_result=None,
        visual_memory=None,
        semantic_list=None,
    ) -> dict:
        bx, by = world.baby_pos

        # Posiciones dinamicas con fallback para mocks de tests
        _key_pos = getattr(world, "key_pos", _KEY_POS_DEFAULT)
        _prog_pos = getattr(world, "progress_door_pos", _PROGRESS_DOOR_DEFAULT)
        _hazards = getattr(world, "_hazard_positions", {})
        _gs = getattr(world, "size", 8)
        max_dist = max((_gs - 1) * 2.0, 1.0)

        kx, ky = _key_pos
        px, py_ = _prog_pos

        key_present = getattr(world, "key_present", True)
        key_dist = (abs(bx - kx) + abs(by - ky)) / max_dist if key_present else 0.0
        prog_dist = (abs(bx - px) + abs(by - py_)) / max_dist

        # Amenaza mas cercana (radio 3) usando posiciones dinamicas del mundo
        nearest_threat = None
        min_td = 999
        for (hx, hy), hid in _hazards.items():
            d = abs(bx - hx) + abs(by - hy)
            if d <= 3 and d < min_td:
                min_td = d
                nearest_threat = hid

        bs = body_state.to_dict() if hasattr(body_state, "to_dict") else {}
        has_shield = float(bs.get("shield", 0.0)) > 0.05

        prog_nearby = (
            world.get_nearby_progress_door()
            if hasattr(world, "get_nearby_progress_door")
            else False
        )
        opt_door_id = (
            world.get_nearby_level_door()
            if hasattr(world, "get_nearby_level_door")
            else None
        )
        opt_nearby = opt_door_id is not None and not prog_nearby

        nearby_powerup = (
            world.get_nearby_powerup() if hasattr(world, "get_nearby_powerup") else None
        )
        should_ignore_optional = inventory.has_key or not key_present
        should_return_home = inventory.energy < 0.2 and not world_manager.is_at_home

        # ── Percepcion 0.4.5b ─────────────────────────────────────────────────
        visible_objects_count = 0
        visible_hazards_count = 0
        visible_rewards_count = 0
        key_visible = False
        progress_door_visible = False
        best_visible_object = None
        most_dangerous_visible = None

        if perception_result:
            visible_objects_count = perception_result.get("total_visible", 0)
            visible_hazards_count = perception_result.get("danger_count", 0)
            visible_rewards_count = perception_result.get("reward_count", 0)
            key_visible = perception_result.get("nearest_key") is not None
            progress_door_visible = (
                perception_result.get("nearest_progress_door") is not None
            )

        if semantic_list:
            from brain.semantic_map import SemanticMap

            _sm = SemanticMap()
            _best = _sm.best_visible_object(semantic_list)
            if _best:
                best_visible_object = {
                    "category": _best.get("category"),
                    "utility": _best.get("utility"),
                    "position": _best.get("position"),
                }
            _most_dangerous = _sm.most_dangerous_visible(semantic_list)
            if _most_dangerous:
                most_dangerous_visible = {
                    "category": _most_dangerous.get("category"),
                    "risk": _most_dangerous.get("risk"),
                    "position": _most_dangerous.get("position"),
                }

        # ── Memoria visual 0.4.5b ─────────────────────────────────────────────
        remembered_key_position = None
        remembered_progress_door_position = None
        if visual_memory:
            remembered_key_position = visual_memory.last_seen_key
            remembered_progress_door_position = visual_memory.last_seen_progress_door

        return {
            "has_key": inventory.has_key,
            "current_goal": mission_state.current_goal,
            "target_position": mission_state.target_position,
            "nearest_threat": nearest_threat,
            "nearest_useful_powerup": nearby_powerup,
            "progress_door_distance": round(prog_dist, 3),
            "key_distance": round(key_dist, 3),
            "progress_door_nearby": prog_nearby,
            "optional_door_nearby": opt_nearby,
            "should_ignore_optional": should_ignore_optional,
            "should_return_home": should_return_home,
            "has_shield": has_shield,
            "energy": round(inventory.energy, 3),
            # Percepcion 0.4.5b
            "visible_objects_count": visible_objects_count,
            "visible_hazards_count": visible_hazards_count,
            "visible_rewards_count": visible_rewards_count,
            "key_visible": key_visible,
            "progress_door_visible": progress_door_visible,
            "best_visible_object": best_visible_object,
            "most_dangerous_visible": most_dangerous_visible,
            "remembered_key_position": remembered_key_position,
            "remembered_progress_door_position": remembered_progress_door_position,
        }
