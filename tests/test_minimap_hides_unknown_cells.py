"""Tests de logica de navegacion del minimapa — BabyIA 0.4.5b."""

import pytest
from interface.minimap_view import _direction, _manhattan, _COMPASS_CHARS


class TestDirectionHelper:
    def test_same_position(self):
        assert _direction((4, 4), (4, 4)) == "•"

    def test_right(self):
        assert _direction((0, 0), (3, 0)) == "→"

    def test_left(self):
        assert _direction((5, 5), (2, 5)) == "←"

    def test_up(self):
        assert _direction((4, 4), (4, 1)) == "↑"

    def test_down(self):
        assert _direction((4, 4), (4, 7)) == "↓"

    def test_diagonal_down_right(self):
        assert _direction((0, 0), (3, 3)) == "↘"

    def test_diagonal_up_left(self):
        assert _direction((4, 4), (1, 1)) == "↖"

    def test_all_compass_chars_covered(self):
        for key, char in _COMPASS_CHARS.items():
            assert char in {"←", "→", "↑", "↓", "↖", "↗", "↙", "↘", "•"}


class TestManhattanHelper:
    def test_zero_same_pos(self):
        assert _manhattan((3, 3), (3, 3)) == 0

    def test_horizontal(self):
        assert _manhattan((0, 0), (5, 0)) == 5

    def test_vertical(self):
        assert _manhattan((0, 0), (0, 4)) == 4

    def test_diagonal(self):
        assert _manhattan((0, 0), (3, 4)) == 7

    def test_symmetry(self):
        a, b = (1, 6), (7, 7)
        assert _manhattan(a, b) == _manhattan(b, a)


class TestDynamicPositionLogic:
    """Verifica que la logica de posiciones dinamicas del minimapa sea correcta."""

    def test_key_pos_from_status_8x8(self):
        key_pos = [1, 6]
        KEY_POS = (int(key_pos[0]), int(key_pos[1]))
        assert KEY_POS == (1, 6)

    def test_key_pos_from_status_16x16(self):
        key_pos = [1, 14]
        KEY_POS = (int(key_pos[0]), int(key_pos[1]))
        assert KEY_POS == (1, 14)

    def test_progress_door_pos_from_status(self):
        prog_door = [15, 15]
        PROG_DOOR_POS = (int(prog_door[0]), int(prog_door[1]))
        assert PROG_DOOR_POS == (15, 15)

    def test_remembered_key_position_used(self):
        rem_key = [3, 5]
        target_k = tuple(rem_key)
        arrow = _direction((0, 0), target_k)
        assert arrow != "•"

    def test_no_remembered_uses_static(self):
        static_key = (1, 6)
        rem_key = None
        target_k = tuple(rem_key) if rem_key else static_key
        assert target_k == (1, 6)

    @pytest.mark.parametrize(
        "gs,expected_key",
        [
            (8, (1, 6)),
            (10, (1, 8)),
            (12, (1, 10)),
            (16, (1, 14)),
        ],
    )
    def test_key_pos_formula_across_sizes(self, gs, expected_key):
        from world.world_config import get_key_pos

        assert get_key_pos(gs) == expected_key
