"""Tests para brain/visual_memory.py — BabyIA 0.4.5."""

from brain.visual_memory import VisualMemory


def _perception_with_key(kx, ky, dist=2):
    return {
        "visible_objects": [
            {"kind": "KEY", "position": [kx, ky], "distance": dist, "category": "goal"},
        ],
        "nearest_key": {"position": [kx, ky], "distance": dist},
        "nearest_progress_door": None,
        "nearest_hazard": None,
    }


def _perception_with_hazard(hx, hy, dist=1):
    return {
        "visible_objects": [
            {
                "kind": "HAZARD",
                "position": [hx, hy],
                "distance": dist,
                "category": "danger",
            },
        ],
        "nearest_key": None,
        "nearest_progress_door": None,
        "nearest_hazard": {"position": [hx, hy], "distance": dist},
    }


class TestVisualMemoryReset:
    def test_initial_state_empty(self):
        vm = VisualMemory()
        assert vm.last_seen_key is None
        assert vm.last_seen_progress_door is None
        assert len(vm.last_seen_hazards) == 0
        assert len(vm.seen_positions) == 0

    def test_reset_clears_state(self):
        vm = VisualMemory()
        vm.update(_perception_with_key(1, 6), (0, 5))
        vm.reset_episode()
        assert vm.last_seen_key is None
        assert len(vm.seen_positions) == 0

    def test_reset_clears_times_key_seen(self):
        vm = VisualMemory()
        vm.update(_perception_with_key(1, 6), (0, 5))
        vm.reset_episode()
        assert vm.times_key_seen == 0


class TestVisualMemoryUpdate:
    def test_update_records_baby_pos(self):
        vm = VisualMemory()
        vm.update(
            {
                "visible_objects": [],
                "nearest_key": None,
                "nearest_progress_door": None,
                "nearest_hazard": None,
            },
            (3, 4),
        )
        assert (3, 4) in vm.seen_positions

    def test_update_records_key_seen(self):
        vm = VisualMemory()
        vm.update(_perception_with_key(1, 6), (0, 5))
        assert vm.last_seen_key == [1, 6]

    def test_update_increments_times_key_seen(self):
        vm = VisualMemory()
        vm.update(_perception_with_key(1, 6), (0, 5))
        vm.update(_perception_with_key(1, 6), (1, 5))
        assert vm.times_key_seen == 2

    def test_update_records_hazard_position(self):
        vm = VisualMemory()
        vm.update(_perception_with_hazard(3, 5), (2, 5))
        assert len(vm.last_seen_hazards) == 1

    def test_no_duplicate_hazard_positions(self):
        vm = VisualMemory()
        vm.update(_perception_with_hazard(3, 5), (2, 5))
        vm.update(_perception_with_hazard(3, 5), (2, 5))
        assert len(vm.last_seen_hazards) == 1

    def test_known_safe_includes_baby_pos(self):
        vm = VisualMemory()
        vm.update(
            {
                "visible_objects": [],
                "nearest_key": None,
                "nearest_progress_door": None,
                "nearest_hazard": None,
            },
            (5, 5),
        )
        assert vm.is_known_safe((5, 5))


class TestVisualMemoryHelpers:
    def test_has_seen_key_false_initially(self):
        vm = VisualMemory()
        assert not vm.has_seen_key()

    def test_has_seen_key_true_after_update(self):
        vm = VisualMemory()
        vm.update(_perception_with_key(1, 6), (0, 5))
        assert vm.has_seen_key()

    def test_is_known_safe_false_for_unseen(self):
        vm = VisualMemory()
        assert not vm.is_known_safe((7, 7))

    def test_exploration_ratio_zero_initially(self):
        vm = VisualMemory()
        assert vm.exploration_ratio(8) == 0.0

    def test_exploration_ratio_grows(self):
        vm = VisualMemory()
        vm.update(
            {
                "visible_objects": [],
                "nearest_key": None,
                "nearest_progress_door": None,
                "nearest_hazard": None,
            },
            (0, 0),
        )
        assert vm.exploration_ratio(8) > 0.0

    def test_exploration_ratio_max_one(self):
        vm = VisualMemory()
        for x in range(8):
            for y in range(8):
                vm.update(
                    {
                        "visible_objects": [],
                        "nearest_key": None,
                        "nearest_progress_door": None,
                        "nearest_hazard": None,
                    },
                    (x, y),
                )
        assert vm.exploration_ratio(8) == 1.0


class TestVisualMemoryToDict:
    def test_to_dict_returns_dict(self):
        vm = VisualMemory()
        d = vm.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_has_required_keys(self):
        vm = VisualMemory()
        d = vm.to_dict()
        for key in (
            "seen_positions_count",
            "last_seen_key",
            "last_seen_progress_door",
            "known_safe_count",
            "known_danger_count",
            "times_key_seen",
        ):
            assert key in d
