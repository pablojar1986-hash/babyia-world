"""Tests que VisualMemory recuerda la llave y la puerta vistos — BabyIA 0.4.5b."""

from brain.visual_memory import VisualMemory


def _perception_with_key(key_pos=(3, 4), dist=2):
    return {
        "visible_objects": [],
        "nearest_key": {"position": list(key_pos), "distance": dist},
        "nearest_progress_door": None,
        "nearest_hazard": None,
    }


def _perception_with_door(door_pos=(7, 7), dist=3):
    return {
        "visible_objects": [],
        "nearest_key": None,
        "nearest_progress_door": {"position": list(door_pos), "distance": dist},
        "nearest_hazard": None,
    }


def _perception_empty():
    return {
        "visible_objects": [],
        "nearest_key": None,
        "nearest_progress_door": None,
        "nearest_hazard": None,
    }


class TestVisualMemoryRemembers:
    def test_last_seen_key_none_initially(self):
        vm = VisualMemory()
        assert vm.last_seen_key is None

    def test_remembers_key_after_seeing_it(self):
        vm = VisualMemory()
        vm.update(_perception_with_key((3, 4)), (0, 0))
        assert vm.last_seen_key == [3, 4]

    def test_remembers_progress_door(self):
        vm = VisualMemory()
        vm.update(_perception_with_door((7, 7)), (4, 4))
        assert vm.last_seen_progress_door == [7, 7]

    def test_key_seen_counter_increments(self):
        vm = VisualMemory()
        vm.update(_perception_with_key(), (0, 0))
        vm.update(_perception_with_key(), (1, 0))
        assert vm.times_key_seen == 2

    def test_door_seen_counter_increments(self):
        vm = VisualMemory()
        vm.update(_perception_with_door(), (0, 0))
        vm.update(_perception_with_door(), (1, 0))
        assert vm.times_progress_door_seen == 2

    def test_reset_clears_key(self):
        vm = VisualMemory()
        vm.update(_perception_with_key(), (0, 0))
        vm.reset_episode()
        assert vm.last_seen_key is None
        assert vm.times_key_seen == 0

    def test_reset_clears_door(self):
        vm = VisualMemory()
        vm.update(_perception_with_door(), (0, 0))
        vm.reset_episode()
        assert vm.last_seen_progress_door is None

    def test_has_seen_key_false_before_update(self):
        vm = VisualMemory()
        assert vm.has_seen_key() is False

    def test_has_seen_key_true_after_update(self):
        vm = VisualMemory()
        vm.update(_perception_with_key(), (0, 0))
        assert vm.has_seen_key() is True

    def test_empty_perception_does_not_overwrite_key(self):
        vm = VisualMemory()
        vm.update(_perception_with_key((2, 3)), (0, 0))
        vm.update(_perception_empty(), (1, 0))
        assert vm.last_seen_key == [2, 3]

    def test_seen_positions_includes_baby_pos(self):
        vm = VisualMemory()
        vm.update(_perception_empty(), (3, 5))
        assert (3, 5) in vm.seen_positions

    def test_exploration_ratio_zero_initially(self):
        vm = VisualMemory()
        assert vm.exploration_ratio(8) == 0.0

    def test_exploration_ratio_increases_with_steps(self):
        vm = VisualMemory()
        for x in range(4):
            vm.update(_perception_empty(), (x, 0))
        r = vm.exploration_ratio(8)
        assert r > 0.0
        assert r <= 1.0

    def test_to_dict_includes_key_fields(self):
        vm = VisualMemory()
        vm.update(_perception_with_key(), (0, 0))
        d = vm.to_dict()
        assert "last_seen_key" in d
        assert "times_key_seen" in d
        assert d["times_key_seen"] >= 1
