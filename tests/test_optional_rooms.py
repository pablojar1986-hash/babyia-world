"""Tests 0.4.3: puertas opcionales — no marcan level_completed."""

from world.grid_world import GridWorld
from world.level_doors import attempt_level_door, is_progress_door, LEVEL_DOOR_TYPES


def _move_to(world, col, row):
    world.baby_pos = [col, row]


class TestOptionalRooms:
    def test_treasure_door_does_not_mark_level_completed(self):
        result = attempt_level_door("treasure_door", has_key=False)
        assert result["level_completed"] is False

    def test_training_room_door_does_not_mark_level_completed(self):
        result = attempt_level_door("training_room_door", has_key=False)
        assert result["level_completed"] is False

    def test_only_next_level_door_marks_level_completed(self):
        for door_id in ["treasure_door", "training_room_door"]:
            result = attempt_level_door(door_id, has_key=True)
            assert result["level_completed"] is False

    def test_step_into_treasure_door_sets_entered_treasure(self):
        world = GridWorld()
        world.reset()
        _move_to(world, 3, 7)  # adyacente a (4,7)
        _, _, done, info = world.step(3, has_key=False)  # RIGHT → (4,7)
        assert info.get("entered_treasure_room") is True
        assert info.get("level_completed") is False
        assert done is False  # no termina episodio

    def test_step_into_training_room_sets_entered_training(self):
        world = GridWorld()
        world.reset()
        _move_to(world, 6, 0)  # adyacente a (7,0)
        _, _, done, info = world.step(3, has_key=False)  # RIGHT → (7,0)
        assert info.get("entered_training_room") is True
        assert info.get("level_completed") is False
        assert done is False

    def test_optional_doors_accessible_without_key(self):
        for door_id in ["treasure_door", "training_room_door"]:
            door = LEVEL_DOOR_TYPES[door_id]
            assert door.requires_key is False

    def test_optional_doors_have_positive_reward(self):
        for door_id in ["treasure_door", "training_room_door"]:
            result = attempt_level_door(door_id, has_key=False)
            assert result["reward_delta"] > 0

    def test_next_level_door_is_only_progress_door(self):
        progress_doors = [
            door_id for door_id in LEVEL_DOOR_TYPES if is_progress_door(door_id)
        ]
        assert progress_doors == ["next_level_door"]

    def test_optional_doors_enter_optional_room_info(self):
        world = GridWorld()
        world.reset()
        _move_to(world, 3, 7)
        _, _, _, info = world.step(3, has_key=False)
        assert info.get("entered_optional_room") is not None
