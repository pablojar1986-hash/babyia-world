"""Tests para brain/semantic_map.py — BabyIA 0.4.5."""

from brain.semantic_map import (
    SemanticMap,
    CAT_GOAL_RELATED,
    CAT_REWARD,
    CAT_DANGER,
    CAT_OBSTACLE,
    CAT_UNKNOWN,
    CAT_OPTIONAL,
)


class TestSemanticMapClassify:
    def test_key_is_goal_related(self):
        sm = SemanticMap()
        result = sm.classify("KEY")
        assert result["category"] == CAT_GOAL_RELATED

    def test_danger_is_danger(self):
        sm = SemanticMap()
        result = sm.classify("DANGER")
        assert result["category"] == CAT_DANGER

    def test_food_is_reward(self):
        sm = SemanticMap()
        result = sm.classify("FOOD")
        assert result["category"] == CAT_REWARD

    def test_wall_is_obstacle(self):
        sm = SemanticMap()
        result = sm.classify("WALL")
        assert result["category"] == CAT_OBSTACLE

    def test_optional_door_is_optional(self):
        sm = SemanticMap()
        result = sm.classify("OPTIONAL_DOOR")
        assert result["category"] == CAT_OPTIONAL

    def test_result_has_required_fields(self):
        sm = SemanticMap()
        result = sm.classify("KEY")
        for field in (
            "category",
            "meaning",
            "utility",
            "risk",
            "confidence",
            "object_id",
        ):
            assert field in result

    def test_utility_is_float(self):
        sm = SemanticMap()
        result = sm.classify("FOOD")
        assert isinstance(result["utility"], float)

    def test_risk_is_float(self):
        sm = SemanticMap()
        result = sm.classify("HAZARD")
        assert isinstance(result["risk"], float)

    def test_danger_has_high_risk(self):
        sm = SemanticMap()
        result = sm.classify("DANGER")
        assert result["risk"] > 0.5

    def test_key_has_positive_utility(self):
        sm = SemanticMap()
        result = sm.classify("KEY")
        assert result["utility"] > 0

    def test_unknown_kind_returns_unknown_category(self):
        sm = SemanticMap()
        result = sm.classify("NONEXISTENT_THING")
        assert result["category"] == CAT_UNKNOWN


class TestSemanticMapMissionAdjustment:
    def _mission(self, goal):
        from types import SimpleNamespace

        return SimpleNamespace(current_goal=goal)

    def test_key_utility_boosted_for_find_key(self):
        sm = SemanticMap()
        m = self._mission("FIND_KEY")
        result = sm.classify("KEY", mission_state=m)
        assert result["utility"] == 1.0

    def test_level_door_boosted_for_go_to_door(self):
        sm = SemanticMap()
        m = self._mission("GO_TO_NEXT_LEVEL_DOOR")
        result = sm.classify("LEVEL_DOOR", mission_state=m)
        assert result["utility"] == 1.0

    def test_danger_risk_boosted_for_avoid_danger(self):
        sm = SemanticMap()
        m = self._mission("AVOID_DANGER")
        result = sm.classify("DANGER", mission_state=m)
        assert result["risk"] == 1.0
        assert result["utility"] < 0


class TestSemanticMapClassifyAll:
    def test_returns_list(self):
        sm = SemanticMap()
        perception = {
            "visible_objects": [
                {"kind": "KEY", "position": [1, 6], "distance": 2, "category": "goal"},
                {
                    "kind": "DANGER",
                    "position": [3, 5],
                    "distance": 3,
                    "category": "danger",
                },
            ]
        }
        result = sm.classify_all(perception)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_classify_all_preserves_position(self):
        sm = SemanticMap()
        perception = {
            "visible_objects": [
                {
                    "kind": "FOOD",
                    "position": [6, 2],
                    "distance": 1,
                    "category": "reward",
                },
            ]
        }
        result = sm.classify_all(perception)
        assert result[0]["position"] == [6, 2]

    def test_empty_perception(self):
        sm = SemanticMap()
        result = sm.classify_all({"visible_objects": []})
        assert result == []


class TestSemanticMapBest:
    def test_best_visible_object_max_utility(self):
        sm = SemanticMap()
        items = [
            {"utility": 0.5, "risk": 0.0},
            {"utility": 1.0, "risk": 0.0},
            {"utility": 0.3, "risk": 0.0},
        ]
        best = sm.best_visible_object(items)
        assert best["utility"] == 1.0

    def test_best_visible_object_empty(self):
        sm = SemanticMap()
        assert sm.best_visible_object([]) is None

    def test_most_dangerous_visible(self):
        sm = SemanticMap()
        items = [
            {"risk": 0.1, "utility": 0.5},
            {"risk": 0.9, "utility": -0.8},
            {"risk": 0.5, "utility": -0.5},
        ]
        danger = sm.most_dangerous_visible(items)
        assert danger["risk"] == 0.9

    def test_most_dangerous_none_below_threshold(self):
        sm = SemanticMap()
        items = [{"risk": 0.1}, {"risk": 0.2}]
        assert sm.most_dangerous_visible(items) is None
