"""
brain/semantic_map.py — Clasificacion semantica funcional para BabyIA 0.4.5.

Convierte objetos detectados por PerceptionSystem en significado funcional.
"Entender" = clasificar por utilidad, peligro, objetivo o recompensa.
No implica comprension subjetiva.
"""

from __future__ import annotations

# Categorias semanticas
CAT_GOAL_RELATED = "GOAL_RELATED"
CAT_REWARD = "REWARD"
CAT_DANGER = "DANGER"
CAT_OBSTACLE = "OBSTACLE"
CAT_UNKNOWN = "UNKNOWN"
CAT_OPTIONAL = "OPTIONAL"
CAT_HOME = "HOME"

_KIND_TO_CATEGORY: dict[str, str] = {
    "KEY": CAT_GOAL_RELATED,
    "LEVEL_DOOR": CAT_GOAL_RELATED,
    "GOAL": CAT_GOAL_RELATED,
    "DOOR_CLOSED": CAT_OBSTACLE,
    "DOOR_OPEN": CAT_REWARD,
    "FOOD": CAT_REWARD,
    "POWERUP": CAT_REWARD,
    "DANGER": CAT_DANGER,
    "HAZARD": CAT_DANGER,
    "WALL": CAT_OBSTACLE,
    "OPTIONAL_DOOR": CAT_OPTIONAL,
    "SPECIAL_DOOR": CAT_OPTIONAL,
    "UNKNOWN_OBJECT": CAT_UNKNOWN,
    "EMPTY": CAT_UNKNOWN,
}

_KIND_TO_MEANING: dict[str, str] = {
    "KEY": "objetivo principal — necesaria para avanzar",
    "LEVEL_DOOR": "puerta de progreso — cruzar con llave sube de nivel",
    "GOAL": "posicion objetivo",
    "DOOR_CLOSED": "puerta bloqueada — requiere llave",
    "DOOR_OPEN": "puerta abierta",
    "FOOD": "restaura energia",
    "POWERUP": "mejora estado corporal",
    "DANGER": "zona peligrosa — reduce energia",
    "HAZARD": "hazard activo — efecto corporal negativo",
    "WALL": "obstaculo no pasable",
    "OPTIONAL_DOOR": "sala opcional — no avanza de nivel",
    "SPECIAL_DOOR": "puerta con requisito corporal",
    "UNKNOWN_OBJECT": "objeto no clasificado",
    "EMPTY": "celda libre",
}

_KIND_DEFAULT_UTILITY: dict[str, float] = {
    "KEY": 1.0,
    "LEVEL_DOOR": 1.0,
    "FOOD": 0.6,
    "POWERUP": 0.7,
    "DOOR_OPEN": 0.4,
    "OPTIONAL_DOOR": 0.3,
    "SPECIAL_DOOR": 0.2,
    "DOOR_CLOSED": -0.1,
    "DANGER": -0.8,
    "HAZARD": -0.7,
    "WALL": -0.5,
    "UNKNOWN_OBJECT": 0.1,
    "EMPTY": 0.0,
}

_KIND_DEFAULT_RISK: dict[str, float] = {
    "DANGER": 0.9,
    "HAZARD": 0.8,
    "WALL": 0.0,
    "KEY": 0.0,
    "LEVEL_DOOR": 0.0,
    "FOOD": 0.0,
    "POWERUP": 0.1,
    "OPTIONAL_DOOR": 0.0,
    "SPECIAL_DOOR": 0.1,
    "UNKNOWN_OBJECT": 0.3,
    "EMPTY": 0.0,
}


class SemanticMap:
    """
    Clasifica objetos visibles en categorias funcionales.
    Usa CausalMemory y mision actual para ajustar utilidad.
    """

    def classify(
        self,
        kind: str,
        obj_id: str = "",
        causal_memory=None,
        mission_state=None,
    ) -> dict:
        """Devuelve clasificacion semantica de un objeto."""
        category = _KIND_TO_CATEGORY.get(kind, CAT_UNKNOWN)
        meaning = _KIND_TO_MEANING.get(kind, "desconocido")
        base_utility = _KIND_DEFAULT_UTILITY.get(kind, 0.0)
        risk = _KIND_DEFAULT_RISK.get(kind, 0.0)
        confidence = 0.9 if kind in _KIND_TO_CATEGORY else 0.3

        # Ajustar utilidad segun mision actual
        useful_for = ""
        if mission_state:
            goal = getattr(mission_state, "current_goal", "")
            if goal == "FIND_KEY" and kind == "KEY":
                base_utility = 1.0
                useful_for = "mision_find_key"
            elif goal == "GO_TO_NEXT_LEVEL_DOOR" and kind == "LEVEL_DOOR":
                base_utility = 1.0
                useful_for = "mision_go_to_progress_door"
            elif goal in ("AVOID_DANGER",) and kind in ("DANGER", "HAZARD"):
                risk = 1.0
                base_utility = -1.0
                useful_for = "evitar"

        # Ajustar confianza con memoria causal si existe efecto aprendido
        if causal_memory and obj_id:
            try:
                known = causal_memory.get_effect(obj_id)
                if known:
                    confidence = min(1.0, confidence + 0.1)
                    useful_for = useful_for or known
            except Exception:
                pass

        return {
            "object_id": obj_id or kind.lower(),
            "category": category,
            "meaning": meaning,
            "useful_for": useful_for,
            "risk": round(risk, 3),
            "utility": round(base_utility, 3),
            "confidence": round(confidence, 3),
        }

    def classify_all(
        self, perception_result: dict, causal_memory=None, mission_state=None
    ) -> list[dict]:
        """Clasifica todos los objetos visibles del resultado de percepcion."""
        out = []
        for obj in perception_result.get("visible_objects", []):
            kind = obj.get("kind", "EMPTY")
            sem = self.classify(kind, kind.lower(), causal_memory, mission_state)
            sem["position"] = obj.get("position")
            sem["distance"] = obj.get("distance", 0)
            out.append(sem)
        return out

    def best_visible_object(self, semantic_list: list[dict]) -> dict | None:
        """Objeto con mayor utilidad de la lista semantica."""
        if not semantic_list:
            return None
        return max(semantic_list, key=lambda x: x["utility"])

    def most_dangerous_visible(self, semantic_list: list[dict]) -> dict | None:
        """Objeto con mayor riesgo de la lista semantica."""
        dangerous = [o for o in semantic_list if o["risk"] > 0.3]
        if not dangerous:
            return None
        return max(dangerous, key=lambda x: x["risk"])
