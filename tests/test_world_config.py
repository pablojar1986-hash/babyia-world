"""Tests para world/world_config.py — BabyIA 0.4.5."""

from world.world_config import (
    get_grid_size_for_level,
    get_key_pos,
    get_door_pos,
    get_food_pos,
    get_danger_pos,
    get_unknown_pos,
    get_progress_door_pos,
    get_training_door_pos,
    get_treasure_door_pos,
    get_powerup_positions,
    get_hazard_positions,
    get_special_door_positions,
    get_reserved_positions,
)


class TestGridSizeForLevel:
    def test_level_0_is_8(self):
        assert get_grid_size_for_level(0) == 8

    def test_level_1_is_10(self):
        assert get_grid_size_for_level(1) == 10

    def test_level_2_is_12(self):
        assert get_grid_size_for_level(2) == 12

    def test_level_3_is_14(self):
        assert get_grid_size_for_level(3) == 14

    def test_level_4_is_16(self):
        assert get_grid_size_for_level(4) == 16

    def test_level_99_is_16(self):
        assert get_grid_size_for_level(99) == 16


class TestPositionsFor8x8:
    """Valida que las formulas reproducen las posiciones hardcodeadas del grid 8x8."""

    def test_key_pos(self):
        assert get_key_pos(8) == (1, 6)

    def test_door_pos(self):
        assert get_door_pos(8) == (3, 6)

    def test_food_pos(self):
        assert get_food_pos(8) == (6, 2)

    def test_danger_pos(self):
        assert get_danger_pos(8) == (3, 5)

    def test_unknown_pos(self):
        assert get_unknown_pos(8) == (7, 1)

    def test_progress_door_pos(self):
        assert get_progress_door_pos(8) == (7, 7)

    def test_training_door_pos(self):
        assert get_training_door_pos(8) == (7, 0)

    def test_treasure_door_pos(self):
        assert get_treasure_door_pos(8) == (4, 7)

    def test_powerup_positions_8(self):
        pu = get_powerup_positions(8)
        assert (0, 3) in pu
        assert (4, 0) in pu
        assert (6, 5) in pu
        assert (1, 5) in pu

    def test_hazard_positions_8(self):
        hz = get_hazard_positions(8)
        assert (1, 2) in hz
        assert (0, 6) in hz
        assert (6, 3) in hz

    def test_special_door_positions_8(self):
        sd = get_special_door_positions(8)
        assert (3, 0) in sd
        assert (5, 2) in sd


class TestPositionsScaled:
    """Valida que las posiciones escalan correctamente para grids mas grandes."""

    def test_progress_door_is_corner(self):
        for gs in (8, 10, 12, 14, 16):
            px, py = get_progress_door_pos(gs)
            assert px == gs - 1
            assert py == gs - 1

    def test_key_pos_bottom_left_area(self):
        for gs in (8, 10, 12, 14, 16):
            kx, ky = get_key_pos(gs)
            assert kx == 1
            assert ky == gs - 2

    def test_positions_within_grid(self):
        for gs in (8, 10, 12, 16):
            for fn in [
                get_key_pos,
                get_door_pos,
                get_food_pos,
                get_danger_pos,
                get_unknown_pos,
                get_progress_door_pos,
            ]:
                x, y = fn(gs)
                assert 0 <= x < gs, f"{fn.__name__} x={x} out of {gs}"
                assert 0 <= y < gs, f"{fn.__name__} y={y} out of {gs}"


class TestReservedPositions:
    def test_reserved_includes_start(self):
        reserved = get_reserved_positions(8)
        assert (0, 0) in reserved

    def test_reserved_includes_progress_door(self):
        reserved = get_reserved_positions(8)
        assert (7, 7) in reserved

    def test_reserved_includes_key(self):
        reserved = get_reserved_positions(8)
        assert (1, 6) in reserved

    def test_reserved_is_frozenset(self):
        assert isinstance(get_reserved_positions(8), frozenset)

    def test_reserved_scales_with_grid(self):
        r8 = get_reserved_positions(8)
        r16 = get_reserved_positions(16)
        assert (15, 15) in r16
        assert (15, 15) not in r8
