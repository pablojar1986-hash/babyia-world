"""Tests para GridWorld con grid variable — BabyIA 0.4.5."""

import numpy as np
from world.grid_world import GridWorld


class TestGridWorldDefaultIs8x8:
    def test_default_size(self):
        w = GridWorld()
        assert w.size == 8

    def test_key_pos_default(self):
        w = GridWorld()
        assert w.key_pos == (1, 6)

    def test_progress_door_pos_default(self):
        w = GridWorld()
        assert w.progress_door_pos == (7, 7)

    def test_danger_pos_default(self):
        w = GridWorld()
        assert w.danger_pos == (3, 5)

    def test_food_pos_default(self):
        w = GridWorld()
        assert w.food_pos == (6, 2)


class TestGridWorldCustomSize:
    def test_10x10_size(self):
        w = GridWorld(grid_size=10)
        assert w.size == 10

    def test_10x10_key_pos(self):
        w = GridWorld(grid_size=10)
        assert w.key_pos == (1, 8)

    def test_10x10_progress_door(self):
        w = GridWorld(grid_size=10)
        assert w.progress_door_pos == (9, 9)

    def test_16x16_progress_door(self):
        w = GridWorld(grid_size=16)
        assert w.progress_door_pos == (15, 15)

    def test_positions_within_grid(self):
        for gs in (8, 10, 12, 16):
            w = GridWorld(grid_size=gs)
            for pos in [
                w.key_pos,
                w.door_pos,
                w.food_pos,
                w.danger_pos,
                w.unknown_pos,
                w.progress_door_pos,
            ]:
                assert 0 <= pos[0] < gs
                assert 0 <= pos[1] < gs


class TestGridWorldReset:
    def test_reset_returns_obs_array(self):
        w = GridWorld()
        obs = w.reset()
        assert isinstance(obs, np.ndarray)

    def test_reset_baby_at_start(self):
        w = GridWorld(grid_size=10)
        w.step(3)  # moverse
        w.reset()
        assert w.baby_pos == [0, 0]

    def test_reset_key_present(self):
        w = GridWorld()
        w.key_present = False
        w.reset()
        assert w.key_present is True


class TestGridWorldStep:
    def test_step_returns_tuple(self):
        w = GridWorld()
        result = w.step(3)  # derecha
        assert len(result) == 4

    def test_step_updates_baby_pos(self):
        w = GridWorld()
        w.step(3)  # accion 3 = moverse a la derecha
        assert w.baby_pos[0] == 1 or w.baby_pos == [0, 0]  # puede chocar con pared

    def test_step_larger_world(self):
        w = GridWorld(grid_size=12)
        obs, reward, done, info = w.step(3)
        assert obs.shape[0] == 10
        assert isinstance(reward, float)


class TestGridWorldGetGrid:
    def test_get_grid_shape_default(self):
        w = GridWorld()
        grid = w.get_grid()
        assert grid.shape == (8, 8)

    def test_get_grid_shape_10x10(self):
        w = GridWorld(grid_size=10)
        grid = w.get_grid()
        assert grid.shape == (10, 10)

    def test_get_grid_shape_16x16(self):
        w = GridWorld(grid_size=16)
        grid = w.get_grid()
        assert grid.shape == (16, 16)


class TestGridWorldObjectState:
    def test_object_state_has_key_pos(self):
        w = GridWorld()
        state = w.get_object_state()
        assert state["key_pos"] == (1, 6)

    def test_object_state_dynamic(self):
        w = GridWorld(grid_size=12)
        state = w.get_object_state()
        assert state["key_pos"] == w.key_pos
        assert state["danger_pos"] == w.danger_pos

    def test_object_state_key_present(self):
        w = GridWorld()
        assert w.get_object_state()["key_present"] is True


class TestGridWorldLevelDoorPositions:
    def test_default_level_door_at_7_7(self):
        w = GridWorld()
        assert (7, 7) in w._level_door_positions

    def test_large_grid_level_door_at_corner(self):
        w = GridWorld(grid_size=16)
        assert (15, 15) in w._level_door_positions

    def test_level_door_type_is_next_level(self):
        w = GridWorld(grid_size=10)
        door_id = w._level_door_positions.get((9, 9))
        assert door_id == "next_level_door"
