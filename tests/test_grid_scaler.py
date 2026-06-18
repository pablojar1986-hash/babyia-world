"""Tests para interface/grid_scaler.py — BabyIA 0.4.6c."""

from interface.grid_scaler import (
    get_grid_draw_origin,
    get_scaled_cell_size,
    should_draw_compact_label,
    should_draw_label,
    world_to_fullmap_screen,
)
from interface.layout import GRID_AREA


class TestGetScaledCellSize:
    """El grid_area es (12, 12, 464, 464) segun layout.py."""

    def test_8x8_fits_in_grid_area(self):
        cs = get_scaled_cell_size(GRID_AREA, 8)
        assert cs * 8 <= GRID_AREA[2]
        assert cs * 8 <= GRID_AREA[3]

    def test_10x10_fits_in_grid_area(self):
        cs = get_scaled_cell_size(GRID_AREA, 10)
        assert cs * 10 <= GRID_AREA[2]
        assert cs * 10 <= GRID_AREA[3]

    def test_12x12_fits_in_grid_area(self):
        cs = get_scaled_cell_size(GRID_AREA, 12)
        assert cs * 12 <= GRID_AREA[2]
        assert cs * 12 <= GRID_AREA[3]

    def test_14x14_fits_in_grid_area(self):
        cs = get_scaled_cell_size(GRID_AREA, 14)
        assert cs * 14 <= GRID_AREA[2]
        assert cs * 14 <= GRID_AREA[3]

    def test_16x16_fits_in_grid_area(self):
        cs = get_scaled_cell_size(GRID_AREA, 16)
        assert cs * 16 <= GRID_AREA[2]
        assert cs * 16 <= GRID_AREA[3]

    def test_cell_size_decreases_as_world_grows(self):
        cs8 = get_scaled_cell_size(GRID_AREA, 8)
        cs16 = get_scaled_cell_size(GRID_AREA, 16)
        assert cs8 > cs16, f"8x8 cell_size={cs8} debe ser > 16x16 cell_size={cs16}"

    def test_min_cell_size_respected(self):
        cs = get_scaled_cell_size(GRID_AREA, 16, min_cell_size=20)
        assert cs >= 20

    def test_square_grid_area(self):
        area = (0, 0, 400, 400)
        cs = get_scaled_cell_size(area, 10)
        assert cs == 40
        assert cs * 10 <= 400

    def test_rectangular_grid_area_uses_min_dimension(self):
        area = (0, 0, 400, 200)
        cs = get_scaled_cell_size(area, 10)
        assert cs * 10 <= 200  # dimension menor limita


class TestGetGridDrawOrigin:
    def test_8x8_centered_in_464(self):
        area = (0, 0, 464, 464)
        cs = get_scaled_cell_size(area, 8)
        ox, oy = get_grid_draw_origin(area, 8, cs)
        total = 8 * cs
        margin = (464 - total) // 2
        assert ox == margin
        assert oy == margin

    def test_origin_shifts_with_layout_offset(self):
        gx, gy, gw, gh = GRID_AREA
        cs = get_scaled_cell_size(GRID_AREA, 8)
        ox, oy = get_grid_draw_origin(GRID_AREA, 8, cs)
        assert ox >= gx
        assert oy >= gy

    def test_16x16_origin_inside_grid_area(self):
        gx, gy, gw, gh = GRID_AREA
        cs = get_scaled_cell_size(GRID_AREA, 16)
        ox, oy = get_grid_draw_origin(GRID_AREA, 16, cs)
        assert ox >= gx
        assert oy >= gy
        assert ox + 16 * cs <= gx + gw
        assert oy + 16 * cs <= gy + gh

    def test_world_fits_exactly_when_no_margin(self):
        area = (0, 0, 160, 160)
        cs = get_scaled_cell_size(area, 8)  # 20
        ox, oy = get_grid_draw_origin(area, 8, cs)
        assert ox >= 0
        assert oy >= 0


class TestWorldToFullmapScreen:
    def test_top_left_corner(self):
        origin = (10, 20)
        sx, sy = world_to_fullmap_screen((0, 0), origin, 50)
        assert sx == 10
        assert sy == 20

    def test_non_zero_world_pos(self):
        origin = (0, 0)
        sx, sy = world_to_fullmap_screen((3, 4), origin, 30)
        assert sx == 90
        assert sy == 120

    def test_with_real_layout(self):
        cs = get_scaled_cell_size(GRID_AREA, 8)
        ox, oy = get_grid_draw_origin(GRID_AREA, 8, cs)
        sx, sy = world_to_fullmap_screen((0, 0), (ox, oy), cs)
        assert sx == ox
        assert sy == oy

    def test_avatar_within_map(self):
        cs = get_scaled_cell_size(GRID_AREA, 16)
        ox, oy = get_grid_draw_origin(GRID_AREA, 16, cs)
        gx, gy, gw, gh = GRID_AREA
        for bx, by in [(0, 0), (15, 15), (7, 8)]:
            sx, sy = world_to_fullmap_screen((bx, by), (ox, oy), cs)
            av_cx = sx + cs // 2
            av_cy = sy + cs // 2
            assert gx <= av_cx <= gx + gw, f"avatar x={av_cx} fuera del area"
            assert gy <= av_cy <= gy + gh, f"avatar y={av_cy} fuera del area"


class TestShouldDrawLabel:
    def test_large_cell_draws_label(self):
        assert should_draw_label(40) is True
        assert should_draw_label(58) is True

    def test_small_cell_no_label(self):
        assert should_draw_label(30) is False
        assert should_draw_label(16) is False

    def test_compact_range(self):
        assert should_draw_compact_label(28) is True
        assert should_draw_compact_label(39) is True

    def test_no_compact_below_28(self):
        assert should_draw_compact_label(27) is False

    def test_no_compact_above_or_equal_40(self):
        assert should_draw_compact_label(40) is False
        assert should_draw_compact_label(58) is False
