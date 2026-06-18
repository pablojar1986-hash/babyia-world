"""Tests para VisualMemory — seguimiento de estancamiento (0.4.6b)."""

import pytest
from brain.visual_memory import VisualMemory


@pytest.fixture
def vm():
    m = VisualMemory()
    m.reset_episode()
    return m


class TestRegisterCollision:
    def test_first_collision_not_repeated(self, vm):
        repeated = vm.register_collision((1, 2))
        assert repeated is False

    def test_second_collision_is_repeated(self, vm):
        vm.register_collision((1, 2))
        repeated = vm.register_collision((1, 2))
        assert repeated is True

    def test_different_positions_not_repeated(self, vm):
        vm.register_collision((1, 2))
        repeated = vm.register_collision((3, 4))
        assert repeated is False

    def test_repeated_collision_count_zero_initially(self, vm):
        assert vm.repeated_collision_count == 0

    def test_repeated_collision_count_increments(self, vm):
        vm.register_collision((0, 0))
        vm.register_collision((0, 0))
        vm.register_collision((0, 0))
        assert vm.repeated_collision_count == 2


class TestRegisterHazard:
    def test_first_hazard_not_repeated(self, vm):
        repeated = vm.register_hazard((5, 5))
        assert repeated is False

    def test_second_hazard_is_repeated(self, vm):
        vm.register_hazard((5, 5))
        repeated = vm.register_hazard((5, 5))
        assert repeated is True

    def test_repeated_hazard_count(self, vm):
        vm.register_hazard((2, 3))
        vm.register_hazard((2, 3))
        vm.register_hazard((4, 4))
        assert vm.repeated_hazard_count == 1


class TestRegisterVisit:
    def test_visit_updates_cell_counts(self, vm):
        vm.register_visit((3, 3))
        vm.register_visit((3, 3))
        assert vm._cell_visit_counts.get((3, 3), 0) == 2

    def test_stuck_zone_none_below_threshold(self, vm):
        for _ in range(4):
            vm.register_visit((1, 1))
        assert vm.stuck_zone_hint is None

    def test_stuck_zone_at_threshold(self, vm):
        for _ in range(5):
            vm.register_visit((2, 2))
        assert vm.stuck_zone_hint == (2, 2)

    def test_stuck_zone_most_visited(self, vm):
        for _ in range(3):
            vm.register_visit((1, 1))
        for _ in range(6):
            vm.register_visit((2, 2))
        assert vm.stuck_zone_hint == (2, 2)


class TestRegisterProgress:
    def test_progress_cell_stored(self, vm):
        vm.register_progress((4, 4))
        assert vm.last_progress_cell == (4, 4)

    def test_progress_cell_updated(self, vm):
        vm.register_progress((1, 1))
        vm.register_progress((2, 2))
        assert vm.last_progress_cell == (2, 2)


class TestResetEpisode:
    def test_reset_clears_collision_counts(self, vm):
        vm.register_collision((0, 0))
        vm.register_collision((0, 0))
        vm.reset_episode()
        assert vm.repeated_collision_count == 0

    def test_reset_clears_hazard_counts(self, vm):
        vm.register_hazard((1, 1))
        vm.register_hazard((1, 1))
        vm.reset_episode()
        assert vm.repeated_hazard_count == 0

    def test_reset_clears_stuck_zone(self, vm):
        for _ in range(6):
            vm.register_visit((3, 3))
        vm.reset_episode()
        assert vm.stuck_zone_hint is None

    def test_reset_clears_progress_cell(self, vm):
        vm.register_progress((5, 5))
        vm.reset_episode()
        assert vm.last_progress_cell is None


class TestToDict:
    def test_to_dict_includes_stagnation_keys(self, vm):
        d = vm.to_dict()
        assert "repeated_collision_count" in d
        assert "repeated_hazard_count" in d
        assert "stuck_zone_hint" in d
        assert "last_progress_cell" in d

    def test_stuck_zone_serialized_as_list(self, vm):
        for _ in range(5):
            vm.register_visit((1, 2))
        d = vm.to_dict()
        assert d["stuck_zone_hint"] == [1, 2]

    def test_stuck_zone_none_serialized_as_none(self, vm):
        d = vm.to_dict()
        assert d["stuck_zone_hint"] is None
