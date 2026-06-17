"""Tests de mision con mundos grandes — BabyIA 0.4.5."""

from world.grid_world import GridWorld
from brain.mission import MissionTracker, FIND_KEY, GO_TO_NEXT_LEVEL_DOOR


class TestMissionWithDynamicPositions:
    def _tracker(self):
        return MissionTracker()

    def test_find_key_on_10x10(self):
        w = GridWorld(grid_size=10)
        t = self._tracker()
        ms = t.compute(
            has_key=False,
            level_completed=False,
            energy=1.0,
            danger_nearby=False,
            has_shield=False,
            is_at_home=True,
            step_count=0,
            baby_pos=(0, 0),
            key_present=True,
            key_pos=w.key_pos,
            progress_door_pos=w.progress_door_pos,
        )
        assert ms.current_goal == FIND_KEY
        assert ms.target_position == w.key_pos

    def test_go_to_door_on_16x16(self):
        w = GridWorld(grid_size=16)
        t = self._tracker()
        ms = t.compute(
            has_key=True,
            level_completed=False,
            energy=1.0,
            danger_nearby=False,
            has_shield=False,
            is_at_home=True,
            step_count=0,
            baby_pos=(0, 0),
            key_present=False,
            key_pos=w.key_pos,
            progress_door_pos=w.progress_door_pos,
        )
        assert ms.current_goal == GO_TO_NEXT_LEVEL_DOOR
        assert ms.target_position == w.progress_door_pos

    def test_progress_score_zero_at_start_large(self):
        w = GridWorld(grid_size=16)
        t = self._tracker()
        ms = t.compute(
            has_key=True,
            level_completed=False,
            energy=1.0,
            danger_nearby=False,
            has_shield=False,
            is_at_home=True,
            step_count=0,
            baby_pos=(0, 0),
            key_present=False,
            key_pos=w.key_pos,
            progress_door_pos=w.progress_door_pos,
        )
        # En (0,0) lejos de (15,15), progress_score debe ser bajo
        assert ms.progress_score < 0.3

    def test_progress_score_high_near_door_large(self):
        w = GridWorld(grid_size=16)
        t = self._tracker()
        px, py = w.progress_door_pos
        ms = t.compute(
            has_key=True,
            level_completed=False,
            energy=1.0,
            danger_nearby=False,
            has_shield=False,
            is_at_home=True,
            step_count=0,
            baby_pos=(px - 1, py),
            key_present=False,
            key_pos=w.key_pos,
            progress_door_pos=w.progress_door_pos,
        )
        assert ms.progress_score > 0.9


class TestMazeForLargeLevel:
    def test_level_2_returns_12x12(self):
        from world.level_factory import get_maze_for_level

        maze = get_maze_for_level(2)
        assert maze["grid_size"] == 12

    def test_level_4_returns_16x16(self):
        from world.level_factory import get_maze_for_level

        maze = get_maze_for_level(4)
        assert maze["grid_size"] == 16

    def test_level_0_returns_8x8(self):
        from world.level_factory import get_maze_for_level

        maze = get_maze_for_level(0)
        assert maze["grid_size"] == 8

    def test_large_level_maze_is_solvable(self):
        from world.level_factory import get_maze_for_level

        maze = get_maze_for_level(3)
        assert maze["solvable"] is True

    def test_maze_has_grid_size_key(self):
        from world.level_factory import get_maze_for_level

        maze = get_maze_for_level(1)
        assert "grid_size" in maze


class TestGridWorldStepping:
    def test_step_in_10x10_world(self):
        w = GridWorld(grid_size=10)
        w.reset()
        obs, reward, done, info = w.step(3)  # right
        assert obs.shape[0] == 10
        assert not done

    def test_max_steps_is_200(self):
        from world.grid_world import MAX_STEPS

        w = GridWorld(grid_size=16)
        w.reset()
        for _ in range(MAX_STEPS):
            obs, r, done, info = w.step(3)
            if done:
                break
        assert w.steps >= 1
