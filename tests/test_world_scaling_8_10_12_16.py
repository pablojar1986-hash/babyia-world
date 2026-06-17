"""Tests de escalado de GridWorld en sizes 8, 10, 12, 16 — BabyIA 0.4.5b."""

import pytest
from world.grid_world import GridWorld
from world.world_config import get_key_pos, get_progress_door_pos


@pytest.mark.parametrize("gs", [8, 10, 12, 16])
class TestGridWorldScaling:
    def test_grid_size_attribute(self, gs):
        w = GridWorld(grid_size=gs)
        assert w.size == gs

    def test_key_pos_within_bounds(self, gs):
        w = GridWorld(grid_size=gs)
        kx, ky = w.key_pos
        assert 0 <= kx < gs
        assert 0 <= ky < gs

    def test_progress_door_pos_within_bounds(self, gs):
        w = GridWorld(grid_size=gs)
        px, py = w.progress_door_pos
        assert 0 <= px < gs
        assert 0 <= py < gs

    def test_start_pos_within_bounds(self, gs):
        w = GridWorld(grid_size=gs)
        sx, sy = w.start_pos
        assert 0 <= sx < gs
        assert 0 <= sy < gs

    def test_reset_returns_obs(self, gs):
        w = GridWorld(grid_size=gs)
        obs = w.reset()
        assert obs is not None
        assert len(obs) > 0

    def test_get_grid_shape(self, gs):
        w = GridWorld(grid_size=gs)
        w.reset()
        grid = w.get_grid()
        assert len(grid) == gs
        assert all(len(row) == gs for row in grid)

    def test_positions_differ_across_sizes(self, gs):
        w = GridWorld(grid_size=gs)
        kx, ky = w.key_pos
        px, py = w.progress_door_pos
        assert (kx, ky) != (px, py)

    def test_goal_alias_matches_progress_door(self, gs):
        w = GridWorld(grid_size=gs)
        assert w.goal == w.progress_door_pos

    def test_config_formula_consistency(self, gs):
        expected_key = get_key_pos(gs)
        expected_door = get_progress_door_pos(gs)
        w = GridWorld(grid_size=gs)
        assert w.key_pos == expected_key
        assert w.progress_door_pos == expected_door
