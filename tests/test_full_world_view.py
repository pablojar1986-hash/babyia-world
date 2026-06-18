"""Tests para vista completa del mundo — BabyIA 0.4.6c."""

from interface.grid_scaler import (
    get_scaled_cell_size,
    get_grid_draw_origin,
    world_to_fullmap_screen,
)
from interface.layout import GRID_AREA


def _avatar_screen_pos(world_size, baby_pos):
    """Calcula la posicion del avatar en pantalla para un mundo dado."""
    cs = get_scaled_cell_size(GRID_AREA, world_size)
    ox, oy = get_grid_draw_origin(GRID_AREA, world_size, cs)
    bx, by = baby_pos
    sx, sy = world_to_fullmap_screen((bx, by), (ox, oy), cs)
    return sx + cs // 2, sy + cs // 2, cs


class TestAvatarPositionInFullMode:
    def test_avatar_8x8_top_left_inside_grid(self):
        av_cx, av_cy, _ = _avatar_screen_pos(8, (0, 0))
        gx, gy, gw, gh = GRID_AREA
        assert gx <= av_cx <= gx + gw
        assert gy <= av_cy <= gy + gh

    def test_avatar_8x8_bottom_right_inside_grid(self):
        av_cx, av_cy, _ = _avatar_screen_pos(8, (7, 7))
        gx, gy, gw, gh = GRID_AREA
        assert gx <= av_cx <= gx + gw
        assert gy <= av_cy <= gy + gh

    def test_avatar_16x16_top_left_inside_grid(self):
        av_cx, av_cy, _ = _avatar_screen_pos(16, (0, 0))
        gx, gy, gw, gh = GRID_AREA
        assert gx <= av_cx <= gx + gw
        assert gy <= av_cy <= gy + gh

    def test_avatar_16x16_bottom_right_inside_grid(self):
        av_cx, av_cy, _ = _avatar_screen_pos(16, (15, 15))
        gx, gy, gw, gh = GRID_AREA
        assert gx <= av_cx <= gx + gw
        assert gy <= av_cy <= gy + gh

    def test_avatar_center_12x12(self):
        av_cx, av_cy, _ = _avatar_screen_pos(12, (6, 6))
        gx, gy, gw, gh = GRID_AREA
        assert gx <= av_cx <= gx + gw
        assert gy <= av_cy <= gy + gh


class TestFullMapCoverage:
    def test_all_cells_have_valid_screen_pos_8x8(self):
        ws = 8
        cs = get_scaled_cell_size(GRID_AREA, ws)
        ox, oy = get_grid_draw_origin(GRID_AREA, ws, cs)
        gx, gy, gw, gh = GRID_AREA
        for wy in range(ws):
            for wx in range(ws):
                sx, sy = world_to_fullmap_screen((wx, wy), (ox, oy), cs)
                assert gx <= sx < gx + gw, f"celda ({wx},{wy}) sx={sx} fuera"
                assert gy <= sy < gy + gh, f"celda ({wx},{wy}) sy={sy} fuera"

    def test_all_cells_have_valid_screen_pos_16x16(self):
        ws = 16
        cs = get_scaled_cell_size(GRID_AREA, ws)
        ox, oy = get_grid_draw_origin(GRID_AREA, ws, cs)
        gx, gy, gw, gh = GRID_AREA
        for wy in range(ws):
            for wx in range(ws):
                sx, sy = world_to_fullmap_screen((wx, wy), (ox, oy), cs)
                assert gx <= sx < gx + gw, f"celda ({wx},{wy}) sx={sx} fuera"
                assert gy <= sy < gy + gh, f"celda ({wx},{wy}) sy={sy} fuera"

    def test_full_map_covers_entire_grid_area_8x8(self):
        """El area total cubierta debe aproximarse al GRID_AREA."""
        ws = 8
        cs = get_scaled_cell_size(GRID_AREA, ws)
        covered = ws * cs
        gw = GRID_AREA[2]
        # La cobertura debe ser >= 90% del ancho del area
        assert covered >= gw * 0.9, f"Cobertura {covered}px < 90% de {gw}px"

    def test_full_map_covers_entire_grid_area_16x16(self):
        ws = 16
        cs = get_scaled_cell_size(GRID_AREA, ws)
        covered = ws * cs
        gw = GRID_AREA[2]
        assert covered >= gw * 0.9, f"Cobertura {covered}px < 90% de {gw}px"

    def test_no_overlap_between_adjacent_cells(self):
        """Celdas adyacentes no deben solapar (sx2 >= sx1 + cs)."""
        ws = 10
        cs = get_scaled_cell_size(GRID_AREA, ws)
        ox, oy = get_grid_draw_origin(GRID_AREA, ws, cs)
        for wx in range(ws - 1):
            sx1, _ = world_to_fullmap_screen((wx, 0), (ox, oy), cs)
            sx2, _ = world_to_fullmap_screen((wx + 1, 0), (ox, oy), cs)
            assert sx2 == sx1 + cs, f"Celda {wx} y {wx+1} no son contiguas"
