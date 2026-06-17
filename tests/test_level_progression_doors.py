"""Tests 0.4.3: puertas de nivel — bloqueo, apertura y level_completed."""

from world.grid_world import GridWorld
from world.level_doors import (
    LEVEL_DOOR_POSITIONS,
    LEVEL_DOOR_TYPES,
    attempt_level_door,
    is_progress_door,
)


def _move_to(world, target_col, target_row):
    """Fuerza la posicion de BabyIA (solo para tests)."""
    world.baby_pos = [target_col, target_row]


class TestAttemptLevelDoor:
    def test_next_level_door_blocked_without_key(self):
        result = attempt_level_door("next_level_door", has_key=False)
        assert result["can_pass"] is False
        assert result["level_completed"] is False
        assert result["blocked_reason"] != ""

    def test_next_level_door_passes_with_key(self):
        result = attempt_level_door("next_level_door", has_key=True)
        assert result["can_pass"] is True
        assert result["level_completed"] is True

    def test_treasure_door_passes_without_key(self):
        result = attempt_level_door("treasure_door", has_key=False)
        assert result["can_pass"] is True
        assert result["level_completed"] is False

    def test_training_room_door_passes_without_key(self):
        result = attempt_level_door("training_room_door", has_key=False)
        assert result["can_pass"] is True
        assert result["level_completed"] is False

    def test_unknown_door_returns_blocked(self):
        result = attempt_level_door("nonexistent_door", has_key=True)
        assert result["can_pass"] is False

    def test_next_level_door_has_penalty_when_blocked(self):
        door = LEVEL_DOOR_TYPES["next_level_door"]
        result = attempt_level_door("next_level_door", has_key=False)
        assert result["reward_delta"] == door.penalty_on_blocked
        assert result["reward_delta"] < 0

    def test_next_level_door_has_reward_when_open(self):
        result = attempt_level_door("next_level_door", has_key=True)
        assert result["reward_delta"] > 0

    def test_is_progress_door_next_level(self):
        assert is_progress_door("next_level_door") is True

    def test_is_progress_door_optional(self):
        assert is_progress_door("treasure_door") is False
        assert is_progress_door("training_room_door") is False

    def test_is_progress_door_unknown(self):
        assert is_progress_door("does_not_exist") is False


class TestGridWorldLevelDoors:
    def test_step_to_next_level_without_key_blocked(self):
        world = GridWorld()
        world.reset()
        _move_to(world, 6, 7)  # adyacente a (7,7)
        _, _, done, info = world.step(3, has_key=False)  # RIGHT → (7,7)
        assert info["hit_next_level_door"] is True
        assert info["level_completed"] is False
        assert done is False  # no termina el episodio

    def test_step_to_next_level_with_key_completes_level(self):
        world = GridWorld()
        world.reset()
        world.key_present = False  # simular que ya tiene la llave
        _move_to(world, 6, 7)
        _, _, done, info = world.step(3, has_key=True)  # RIGHT → (7,7)
        assert info["level_completed"] is True
        assert info["next_level_door_opened"] is True
        assert done is True

    def test_level_door_positions_has_three_doors(self):
        assert len(LEVEL_DOOR_POSITIONS) >= 3

    def test_next_level_door_at_goal_pos(self):
        assert (7, 7) in LEVEL_DOOR_POSITIONS
        assert LEVEL_DOOR_POSITIONS[(7, 7)] == "next_level_door"

    def test_get_grid_shows_level_door_cell(self):
        from world.objects import Cell

        world = GridWorld()
        world.reset()
        grid = world.get_grid()
        assert grid[7][7] == int(Cell.LEVEL_DOOR)

    def test_get_grid_shows_optional_door_cell(self):
        from world.objects import Cell

        world = GridWorld()
        world.reset()
        grid = world.get_grid()
        # (4,7) treasure_door → OPTIONAL_DOOR
        assert grid[7][4] == int(Cell.OPTIONAL_DOOR)
