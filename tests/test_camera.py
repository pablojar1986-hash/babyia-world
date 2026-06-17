"""Tests para interface/camera.py — BabyIA 0.4.5."""

from interface.camera import Camera


class TestCameraInit:
    def test_default_viewport(self):
        cam = Camera()
        assert cam.viewport == 8

    def test_custom_viewport(self):
        cam = Camera(viewport_cells=10)
        assert cam.viewport == 10

    def test_initial_offset_zero(self):
        cam = Camera()
        assert cam.offset == (0, 0)


class TestCameraUpdateSmallGrid:
    """Si grid <= viewport, offset siempre es (0,0)."""

    def test_small_grid_offset_zero(self):
        cam = Camera(viewport_cells=8)
        cam.update((3, 3), grid_size=8)
        assert cam.offset == (0, 0)

    def test_equal_size_offset_zero(self):
        cam = Camera(viewport_cells=10)
        cam.update((5, 5), grid_size=10)
        assert cam.offset == (0, 0)


class TestCameraUpdateLargeGrid:
    """Si grid > viewport, la camara sigue al avatar."""

    def test_center_of_large_grid(self):
        cam = Camera(viewport_cells=8)
        cam.update((8, 8), grid_size=16)
        ox, oy = cam.offset
        # Baby at 8: offset should center at 8 - 4 = 4
        assert ox == 4
        assert oy == 4

    def test_clamp_top_left(self):
        cam = Camera(viewport_cells=8)
        cam.update((0, 0), grid_size=16)
        assert cam.offset == (0, 0)

    def test_clamp_bottom_right(self):
        cam = Camera(viewport_cells=8)
        cam.update((15, 15), grid_size=16)
        ox, oy = cam.offset
        assert ox == 8  # max offset = 16 - 8 = 8
        assert oy == 8


class TestCameraIsVisible:
    def test_visible_in_small_grid(self):
        cam = Camera(viewport_cells=8)
        cam.update((3, 3), grid_size=8)
        assert cam.is_visible(0, 0)
        assert cam.is_visible(7, 7)

    def test_visible_in_viewport(self):
        cam = Camera(viewport_cells=8)
        cam.update((8, 8), grid_size=16)
        ox, oy = cam.offset
        assert cam.is_visible(ox, oy)
        assert cam.is_visible(ox + 7, oy + 7)

    def test_not_visible_outside_viewport(self):
        cam = Camera(viewport_cells=8)
        cam.update((8, 8), grid_size=16)
        ox, oy = cam.offset
        assert not cam.is_visible(ox - 1, oy)


class TestCameraGetVisibleBounds:
    def test_bounds_small_grid(self):
        cam = Camera(viewport_cells=8)
        cam.update((3, 3), grid_size=8)
        mn_x, mn_y, mx_x, mx_y = cam.get_visible_bounds()
        assert mn_x == 0
        assert mn_y == 0
        assert mx_x == 8
        assert mx_y == 8

    def test_bounds_large_grid_clamped(self):
        cam = Camera(viewport_cells=8)
        cam.update((8, 8), grid_size=16)
        mn_x, mn_y, mx_x, mx_y = cam.get_visible_bounds()
        assert mx_x - mn_x <= 8
        assert mx_y - mn_y <= 8


class TestCameraWorldToScreen:
    def test_origin_cell(self):
        cam = Camera(viewport_cells=8)
        cam.update((0, 0), grid_size=8)
        sx, sy = cam.world_to_screen(0, 0, cell_size=58, origin_x=12, origin_y=12)
        assert sx == 12
        assert sy == 12

    def test_offset_applied(self):
        cam = Camera(viewport_cells=8)
        cam.update((8, 8), grid_size=16)
        ox, oy = cam.offset
        sx, sy = cam.world_to_screen(ox, oy, cell_size=58, origin_x=0, origin_y=0)
        assert sx == 0
        assert sy == 0
