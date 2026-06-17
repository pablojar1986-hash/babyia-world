"""Tests de limites del viewport de camara — BabyIA 0.4.5b."""

import pytest
from interface.camera import Camera


@pytest.mark.parametrize("gs", [8, 10, 12, 16])
class TestCameraViewportBounds:
    def test_offset_never_negative(self, gs):
        cam = Camera(viewport_cells=8)
        cam.update((0, 0), grid_size=gs)
        ox, oy = cam.offset
        assert ox >= 0
        assert oy >= 0

    def test_offset_never_exceeds_grid(self, gs):
        cam = Camera(viewport_cells=8)
        cam.update((gs - 1, gs - 1), grid_size=gs)
        ox, oy = cam.offset
        assert ox <= max(0, gs - 8)
        assert oy <= max(0, gs - 8)

    def test_visible_bounds_within_grid(self, gs):
        cam = Camera(viewport_cells=8)
        for bx, by in [(0, 0), (gs // 2, gs // 2), (gs - 1, gs - 1)]:
            cam.update((bx, by), grid_size=gs)
            mn_x, mn_y, mx_x, mx_y = cam.get_visible_bounds()
            assert mn_x >= 0
            assert mn_y >= 0
            assert mx_x <= gs
            assert mx_y <= gs

    def test_viewport_size_capped(self, gs):
        cam = Camera(viewport_cells=8)
        cam.update((gs // 2, gs // 2), grid_size=gs)
        mn_x, mn_y, mx_x, mx_y = cam.get_visible_bounds()
        assert mx_x - mn_x <= 8
        assert mx_y - mn_y <= 8

    def test_small_grid_no_scroll(self, gs):
        if gs > 8:
            pytest.skip("only for grid <= viewport")
        cam = Camera(viewport_cells=8)
        cam.update((gs // 2, gs // 2), grid_size=gs)
        assert cam.offset == (0, 0)


class TestCameraLargeGridScrolling:
    def test_scrolls_in_large_grid(self):
        cam = Camera(viewport_cells=8)
        cam.update((12, 12), grid_size=16)
        ox, oy = cam.offset
        assert ox > 0 or oy > 0

    def test_baby_always_visible_after_update(self):
        cam = Camera(viewport_cells=8)
        for bx in range(16):
            cam.update((bx, 8), grid_size=16)
            assert cam.is_visible(bx, 8)

    def test_offset_monotone_as_baby_moves_right(self):
        cam = Camera(viewport_cells=8)
        prev_ox = -1
        for bx in range(16):
            cam.update((bx, 0), grid_size=16)
            ox, _ = cam.offset
            assert ox >= prev_ox
            prev_ox = ox
