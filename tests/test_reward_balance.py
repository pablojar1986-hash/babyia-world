"""Tests 0.4.3: balance de recompensas — completion debe superar exploracion."""

from world.rewards import (
    REWARD_NEW_CELL,
    REWARD_LEVEL_COMPLETED,
    REWARD_NEXT_LEVEL_DOOR,
    REWARD_TREASURE_ROOM,
    REWARD_TRAINING_ROOM,
    REWARD_NEXT_DOOR_WITHOUT_KEY,
    REWARD_KEY_FIRST,
    calculate_reward,
    object_reward,
)

GRID_SIZE = 8
MAX_CELLS = GRID_SIZE * GRID_SIZE


class TestRewardBalance:
    def test_level_completed_exceeds_full_exploration(self):
        max_exploration = MAX_CELLS * REWARD_NEW_CELL
        assert REWARD_LEVEL_COMPLETED > max_exploration, (
            f"REWARD_LEVEL_COMPLETED={REWARD_LEVEL_COMPLETED} debe superar "
            f"exploracion_max={max_exploration}"
        )

    def test_new_cell_reward_is_reduced(self):
        assert (
            REWARD_NEW_CELL <= 0.1
        ), f"REWARD_NEW_CELL={REWARD_NEW_CELL} debe ser <= 0.1 para evitar reward hacking"

    def test_key_first_reward_is_significant(self):
        assert REWARD_KEY_FIRST >= 3.0

    def test_next_level_door_reward_is_positive(self):
        assert REWARD_NEXT_LEVEL_DOOR > 0

    def test_next_door_without_key_is_penalty(self):
        assert REWARD_NEXT_DOOR_WITHOUT_KEY < 0

    def test_treasure_room_is_optional_bonus(self):
        assert 0 < REWARD_TREASURE_ROOM < REWARD_LEVEL_COMPLETED

    def test_training_room_is_optional_bonus(self):
        assert 0 < REWARD_TRAINING_ROOM < REWARD_TREASURE_ROOM

    def test_object_reward_level_completed(self):
        r = object_reward("level_completed")
        assert r == REWARD_LEVEL_COMPLETED

    def test_object_reward_next_level_door_opened(self):
        r = object_reward("next_level_door_opened")
        assert r == REWARD_NEXT_LEVEL_DOOR

    def test_object_reward_treasure_room(self):
        r = object_reward("treasure_room_entered")
        assert r == REWARD_TREASURE_ROOM

    def test_object_reward_training_room(self):
        r = object_reward("training_room_entered")
        assert r == REWARD_TRAINING_ROOM

    def test_object_reward_next_door_without_key(self):
        r = object_reward("next_door_without_key")
        assert r == REWARD_NEXT_DOOR_WITHOUT_KEY

    def test_calculate_reward_base_step(self):
        r = calculate_reward(False, False, False, [0, 1, 2])
        assert r < 0  # penalty por paso

    def test_level_completed_dominates_100_episodes_of_exploration(self):
        # 100 episodios x 64 celdas x REWARD_NEW_CELL
        exploration_100ep = 100 * MAX_CELLS * REWARD_NEW_CELL
        # 1 nivel completado
        assert (
            REWARD_LEVEL_COMPLETED > exploration_100ep * 0.1
        ), "Completar un nivel debe valer mas que 10 episodios completos de exploracion"
