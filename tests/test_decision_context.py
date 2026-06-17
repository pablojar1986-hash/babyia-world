"""Tests 0.4.4: DecisionContext.build() produce dict correcto."""

from types import SimpleNamespace
from brain.decision_context import DecisionContext
from brain.mission import MissionState, FIND_KEY, GO_TO_NEXT_LEVEL_DOOR, KEY_POS


def _make_world(baby_pos=(0, 0), key_present=True):
    w = SimpleNamespace()
    w.baby_pos = baby_pos
    w.key_present = key_present
    w.get_nearby_progress_door = lambda: False
    w.get_nearby_level_door = lambda: None
    w.get_nearby_powerup = lambda: None
    return w


def _make_inventory(has_key=False, energy=1.0):
    inv = SimpleNamespace()
    inv.has_key = has_key
    inv.energy = energy
    return inv


def _make_body_state(shield=0.0):
    bs = SimpleNamespace()
    bs.to_dict = lambda: {"shield": shield}
    return bs


def _make_world_manager(is_at_home=True):
    wm = SimpleNamespace()
    wm.is_at_home = is_at_home
    return wm


def _make_mission(goal=FIND_KEY, target=KEY_POS):
    return MissionState(current_goal=goal, target_position=target)


class TestDecisionContextBuild:
    def test_returns_dict(self):
        dc = DecisionContext()
        result = dc.build(
            _make_world(),
            _make_inventory(),
            _make_body_state(),
            _make_world_manager(),
            _make_mission(),
        )
        assert isinstance(result, dict)

    def test_has_key_reflects_inventory(self):
        dc = DecisionContext()
        inv_no_key = _make_inventory(has_key=False)
        ctx = dc.build(
            _make_world(),
            inv_no_key,
            _make_body_state(),
            _make_world_manager(),
            _make_mission(),
        )
        assert ctx["has_key"] is False

    def test_has_key_true_when_picked(self):
        dc = DecisionContext()
        inv_with_key = _make_inventory(has_key=True)
        ctx = dc.build(
            _make_world(key_present=False),
            inv_with_key,
            _make_body_state(),
            _make_world_manager(),
            _make_mission(goal=GO_TO_NEXT_LEVEL_DOOR),
        )
        assert ctx["has_key"] is True

    def test_current_goal_from_mission(self):
        dc = DecisionContext()
        ms = _make_mission(goal=GO_TO_NEXT_LEVEL_DOOR)
        ctx = dc.build(
            _make_world(),
            _make_inventory(has_key=True),
            _make_body_state(),
            _make_world_manager(),
            ms,
        )
        assert ctx["current_goal"] == GO_TO_NEXT_LEVEL_DOOR

    def test_key_distance_zero_when_no_key(self):
        dc = DecisionContext()
        ctx = dc.build(
            _make_world(key_present=False),
            _make_inventory(),
            _make_body_state(),
            _make_world_manager(),
            _make_mission(),
        )
        assert ctx["key_distance"] == 0.0

    def test_key_distance_positive_when_key_present(self):
        dc = DecisionContext()
        ctx = dc.build(
            _make_world(baby_pos=(0, 0), key_present=True),
            _make_inventory(),
            _make_body_state(),
            _make_world_manager(),
            _make_mission(),
        )
        assert ctx["key_distance"] > 0.0

    def test_progress_door_distance_decreases_closer(self):
        dc = DecisionContext()
        far = dc.build(
            _make_world(baby_pos=(0, 0)),
            _make_inventory(),
            _make_body_state(),
            _make_world_manager(),
            _make_mission(),
        )
        near = dc.build(
            _make_world(baby_pos=(7, 7)),
            _make_inventory(),
            _make_body_state(),
            _make_world_manager(),
            _make_mission(),
        )
        assert near["progress_door_distance"] < far["progress_door_distance"]

    def test_energy_reflected_from_inventory(self):
        dc = DecisionContext()
        inv = _make_inventory(energy=0.42)
        ctx = dc.build(
            _make_world(),
            inv,
            _make_body_state(),
            _make_world_manager(),
            _make_mission(),
        )
        assert abs(ctx["energy"] - 0.42) < 0.01

    def test_has_shield_false_when_no_shield(self):
        dc = DecisionContext()
        ctx = dc.build(
            _make_world(),
            _make_inventory(),
            _make_body_state(shield=0.0),
            _make_world_manager(),
            _make_mission(),
        )
        assert ctx["has_shield"] is False

    def test_has_shield_true_when_shield_active(self):
        dc = DecisionContext()
        ctx = dc.build(
            _make_world(),
            _make_inventory(),
            _make_body_state(shield=1.0),
            _make_world_manager(),
            _make_mission(),
        )
        assert ctx["has_shield"] is True

    def test_should_return_home_when_low_energy_away(self):
        dc = DecisionContext()
        inv = _make_inventory(energy=0.1)
        wm = _make_world_manager(is_at_home=False)
        ctx = dc.build(
            _make_world(),
            inv,
            _make_body_state(),
            wm,
            _make_mission(),
        )
        assert ctx["should_return_home"] is True

    def test_no_return_home_when_at_home(self):
        dc = DecisionContext()
        inv = _make_inventory(energy=0.1)
        wm = _make_world_manager(is_at_home=True)
        ctx = dc.build(
            _make_world(),
            inv,
            _make_body_state(),
            wm,
            _make_mission(),
        )
        assert ctx["should_return_home"] is False

    def test_required_keys_present(self):
        dc = DecisionContext()
        ctx = dc.build(
            _make_world(),
            _make_inventory(),
            _make_body_state(),
            _make_world_manager(),
            _make_mission(),
        )
        required = [
            "has_key",
            "current_goal",
            "target_position",
            "nearest_threat",
            "nearest_useful_powerup",
            "progress_door_distance",
            "key_distance",
            "progress_door_nearby",
            "optional_door_nearby",
            "should_ignore_optional",
            "should_return_home",
            "has_shield",
            "energy",
        ]
        for key in required:
            assert key in ctx, f"Falta clave: {key}"
