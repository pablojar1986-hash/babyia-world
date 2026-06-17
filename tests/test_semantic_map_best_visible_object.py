"""Tests de SemanticMap.best_visible_object y most_dangerous_visible — BabyIA 0.4.5b."""

import pytest
from brain.semantic_map import SemanticMap, CAT_GOAL_RELATED, CAT_DANGER, CAT_REWARD


@pytest.fixture
def sm():
    return SemanticMap()


def _sem(kind, utility, risk=0.0, position=None, distance=1):
    return {
        "object_id": kind.lower(),
        "category": (
            CAT_GOAL_RELATED
            if kind in ("KEY", "LEVEL_DOOR")
            else (CAT_DANGER if kind in ("DANGER", "HAZARD") else CAT_REWARD)
        ),
        "utility": utility,
        "risk": risk,
        "position": position or [0, 0],
        "distance": distance,
    }


class TestBestVisibleObject:
    def test_returns_none_for_empty_list(self, sm):
        assert sm.best_visible_object([]) is None

    def test_returns_single_item(self, sm):
        items = [_sem("KEY", 1.0)]
        assert sm.best_visible_object(items)["utility"] == 1.0

    def test_returns_highest_utility(self, sm):
        items = [_sem("FOOD", 0.6), _sem("KEY", 1.0), _sem("POWERUP", 0.7)]
        best = sm.best_visible_object(items)
        assert best["utility"] == 1.0

    def test_returns_correct_item(self, sm):
        items = [_sem("FOOD", 0.6, position=[1, 1]), _sem("KEY", 1.0, position=[3, 3])]
        best = sm.best_visible_object(items)
        assert best["position"] == [3, 3]

    def test_all_equal_utility_returns_one(self, sm):
        items = [_sem("FOOD", 0.6), _sem("POWERUP", 0.6)]
        best = sm.best_visible_object(items)
        assert best is not None
        assert best["utility"] == 0.6


class TestMostDangerousVisible:
    def test_returns_none_for_empty_list(self, sm):
        assert sm.most_dangerous_visible([]) is None

    def test_returns_none_when_no_dangerous(self, sm):
        items = [_sem("KEY", 1.0, risk=0.0), _sem("FOOD", 0.6, risk=0.0)]
        assert sm.most_dangerous_visible(items) is None

    def test_returns_highest_risk(self, sm):
        items = [_sem("HAZARD", -0.7, risk=0.8), _sem("DANGER", -0.8, risk=0.9)]
        most = sm.most_dangerous_visible(items)
        assert most["risk"] == 0.9

    def test_filters_low_risk(self, sm):
        items = [_sem("POWERUP", 0.7, risk=0.1), _sem("HAZARD", -0.7, risk=0.8)]
        most = sm.most_dangerous_visible(items)
        assert most["risk"] == 0.8

    def test_threshold_at_0_3(self, sm):
        items = [_sem("DANGER", -0.8, risk=0.3)]
        # risk=0.3 is NOT > 0.3, so should be filtered
        assert sm.most_dangerous_visible(items) is None

    def test_above_threshold_returned(self, sm):
        items = [_sem("DANGER", -0.8, risk=0.31)]
        assert sm.most_dangerous_visible(items) is not None


class TestClassifyAll:
    def test_empty_perception(self, sm):
        result = sm.classify_all({"visible_objects": []})
        assert result == []

    def test_classifies_each_object(self, sm):
        perc = {
            "visible_objects": [
                {"kind": "KEY", "position": [1, 6], "distance": 3},
                {"kind": "FOOD", "position": [2, 2], "distance": 2},
            ]
        }
        result = sm.classify_all(perc)
        assert len(result) == 2

    def test_key_gets_goal_related_category(self, sm):
        perc = {"visible_objects": [{"kind": "KEY", "position": [1, 6], "distance": 3}]}
        result = sm.classify_all(perc)
        assert result[0]["category"] == CAT_GOAL_RELATED

    def test_hazard_gets_danger_category(self, sm):
        perc = {
            "visible_objects": [{"kind": "HAZARD", "position": [3, 3], "distance": 2}]
        }
        result = sm.classify_all(perc)
        assert result[0]["category"] == CAT_DANGER

    def test_position_preserved(self, sm):
        perc = {
            "visible_objects": [{"kind": "FOOD", "position": [5, 5], "distance": 1}]
        }
        result = sm.classify_all(perc)
        assert result[0]["position"] == [5, 5]
