"""Tests que DecisionContext incluye datos de percepcion — BabyIA 0.4.5b."""

import types
from brain.decision_context import DecisionContext
from brain.mission import MissionState
from brain.visual_memory import VisualMemory


def _world(baby_pos=(4, 4)):
    return types.SimpleNamespace(
        baby_pos=list(baby_pos),
        key_pos=(1, 6),
        progress_door_pos=(7, 7),
        _hazard_positions={},
        size=8,
        key_present=True,
        get_nearby_progress_door=lambda: False,
        get_nearby_level_door=lambda: None,
        get_nearby_powerup=lambda: None,
    )


def _inventory(has_key=False, energy=1.0):
    return types.SimpleNamespace(has_key=has_key, energy=energy)


def _body():
    return types.SimpleNamespace(to_dict=lambda: {"shield": 0.0})


def _wm():
    return types.SimpleNamespace(is_at_home=True)


def _ms():
    return MissionState()


class TestDecisionContextUsesPerception:
    def test_no_perception_defaults(self):
        dc = DecisionContext()
        ctx = dc.build(_world(), _inventory(), _body(), _wm(), _ms())
        assert ctx["visible_objects_count"] == 0
        assert ctx["key_visible"] is False
        assert ctx["progress_door_visible"] is False

    def test_key_visible_when_nearest_key_present(self):
        dc = DecisionContext()
        perc = {
            "total_visible": 1,
            "danger_count": 0,
            "reward_count": 0,
            "nearest_key": {"position": [1, 6], "distance": 3},
            "nearest_progress_door": None,
        }
        ctx = dc.build(
            _world(), _inventory(), _body(), _wm(), _ms(), perception_result=perc
        )
        assert ctx["key_visible"] is True

    def test_key_not_visible_when_absent(self):
        dc = DecisionContext()
        perc = {
            "total_visible": 0,
            "danger_count": 0,
            "reward_count": 0,
            "nearest_key": None,
            "nearest_progress_door": None,
        }
        ctx = dc.build(
            _world(), _inventory(), _body(), _wm(), _ms(), perception_result=perc
        )
        assert ctx["key_visible"] is False

    def test_progress_door_visible(self):
        dc = DecisionContext()
        perc = {
            "total_visible": 1,
            "danger_count": 0,
            "reward_count": 0,
            "nearest_key": None,
            "nearest_progress_door": {"position": [7, 7], "distance": 4},
        }
        ctx = dc.build(
            _world(), _inventory(), _body(), _wm(), _ms(), perception_result=perc
        )
        assert ctx["progress_door_visible"] is True

    def test_visible_objects_count(self):
        dc = DecisionContext()
        perc = {
            "total_visible": 5,
            "danger_count": 1,
            "reward_count": 2,
            "nearest_key": None,
            "nearest_progress_door": None,
        }
        ctx = dc.build(
            _world(), _inventory(), _body(), _wm(), _ms(), perception_result=perc
        )
        assert ctx["visible_objects_count"] == 5

    def test_visible_hazards_count(self):
        dc = DecisionContext()
        perc = {
            "total_visible": 3,
            "danger_count": 2,
            "reward_count": 0,
            "nearest_key": None,
            "nearest_progress_door": None,
        }
        ctx = dc.build(
            _world(), _inventory(), _body(), _wm(), _ms(), perception_result=perc
        )
        assert ctx["visible_hazards_count"] == 2

    def test_visible_rewards_count(self):
        dc = DecisionContext()
        perc = {
            "total_visible": 3,
            "danger_count": 0,
            "reward_count": 3,
            "nearest_key": None,
            "nearest_progress_door": None,
        }
        ctx = dc.build(
            _world(), _inventory(), _body(), _wm(), _ms(), perception_result=perc
        )
        assert ctx["visible_rewards_count"] == 3

    def test_remembered_key_from_visual_memory(self):
        dc = DecisionContext()
        vm = VisualMemory()
        vm.last_seen_key = [2, 5]
        ctx = dc.build(_world(), _inventory(), _body(), _wm(), _ms(), visual_memory=vm)
        assert ctx["remembered_key_position"] == [2, 5]

    def test_remembered_door_from_visual_memory(self):
        dc = DecisionContext()
        vm = VisualMemory()
        vm.last_seen_progress_door = [7, 7]
        ctx = dc.build(_world(), _inventory(), _body(), _wm(), _ms(), visual_memory=vm)
        assert ctx["remembered_progress_door_position"] == [7, 7]

    def test_remembered_positions_none_when_no_memory(self):
        dc = DecisionContext()
        ctx = dc.build(_world(), _inventory(), _body(), _wm(), _ms())
        assert ctx["remembered_key_position"] is None
        assert ctx["remembered_progress_door_position"] is None

    def test_all_perception_keys_present(self):
        dc = DecisionContext()
        ctx = dc.build(_world(), _inventory(), _body(), _wm(), _ms())
        expected = [
            "visible_objects_count",
            "visible_hazards_count",
            "visible_rewards_count",
            "key_visible",
            "progress_door_visible",
            "best_visible_object",
            "most_dangerous_visible",
            "remembered_key_position",
            "remembered_progress_door_position",
        ]
        for k in expected:
            assert k in ctx, f"Missing key: {k}"
