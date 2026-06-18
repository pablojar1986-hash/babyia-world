"""Tests de rendering con cámara y consistencia de versión — BabyIA 0.4.5b."""

import inspect
from pathlib import Path


class TestPygameUsesWorldSizeOrCamera:
    """Verifica que pygame_view usa world.size y Camera, no GRID_SIZE fijo."""

    def test_pygame_view_imports_camera(self):
        from interface import pygame_view

        src = inspect.getsource(pygame_view)
        assert "Camera" in src

    def test_pygame_view_does_not_loop_over_fixed_GRID_SIZE(self):
        from interface import pygame_view

        src = inspect.getsource(
            pygame_view._draw_grid
            if hasattr(pygame_view, "_draw_grid")
            else pygame_view.PygameView._draw_grid
        )
        # No debe hacer range(GRID_SIZE) en el loop de dibujo
        assert "range(GRID_SIZE)" not in src

    def test_pygame_view_uses_world_size(self):
        from interface import pygame_view

        src = inspect.getsource(pygame_view.PygameView._draw_grid)
        assert "world_size" in src or "world.size" in src

    def test_pygame_view_uses_camera_update(self):
        """0.4.6c: la logica de camera.update se delega a draw_camera_world."""
        import inspect
        from interface import grid_renderer

        src = inspect.getsource(grid_renderer.draw_camera_world)
        assert "camera.update" in src or ".update(" in src

    def test_pygame_view_has_cam_attribute(self):
        from interface import pygame_view

        src = inspect.getsource(pygame_view.PygameView.__init__)
        assert "_cam" in src and "Camera" in src

    def test_pygame_view_uses_world_to_screen_for_avatar(self):
        """0.4.6c: world_to_screen vive en draw_camera_world de grid_renderer."""
        import inspect
        from interface import grid_renderer

        src = inspect.getsource(grid_renderer.draw_camera_world)
        assert "world_to_screen" in src

    def test_pygame_view_no_bx_times_CELL_SIZE_direct(self):
        """Avatar no debe calcularse con bx * gs directamente (sin cámara)."""
        import inspect
        from interface import grid_renderer

        src = inspect.getsource(grid_renderer.draw_camera_world)
        # La posicion del avatar debe venir de camera.world_to_screen
        assert "world_to_screen" in src
        assert "bx * cell_size" not in src
        assert "by * cell_size" not in src


class TestAvatarPositionUsesCamera:
    """Verifica que Camera.world_to_screen calcula coordenadas correctas."""

    def test_avatar_at_origin_no_offset(self):
        from interface.camera import Camera

        cam = Camera(viewport_cells=8)
        cam.update((0, 0), grid_size=8)
        sx, sy = cam.world_to_screen(0, 0, cell_size=58, origin_x=12, origin_y=12)
        assert sx == 12
        assert sy == 12

    def test_avatar_center_small_grid(self):
        from interface.camera import Camera

        cam = Camera(viewport_cells=8)
        cam.update((4, 4), grid_size=8)
        sx, sy = cam.world_to_screen(4, 4, cell_size=58, origin_x=12, origin_y=12)
        assert sx == 12 + 4 * 58
        assert sy == 12 + 4 * 58

    def test_camera_follows_baby_large_grid(self):
        from interface.camera import Camera

        cam = Camera(viewport_cells=8)
        cam.update((12, 12), grid_size=16)
        ox, oy = cam.offset
        sx, sy = cam.world_to_screen(12, 12, cell_size=58, origin_x=12, origin_y=12)
        # Baby debe estar dentro del viewport
        assert 12 <= sx < 12 + 8 * 58
        assert 12 <= sy < 12 + 8 * 58

    def test_avatar_never_at_negative_screen_pos(self):
        from interface.camera import Camera

        cam = Camera(viewport_cells=8)
        for bx in range(0, 16, 2):
            cam.update((bx, 0), grid_size=16)
            sx, sy = cam.world_to_screen(bx, 0, cell_size=58, origin_x=12, origin_y=12)
            assert sx >= 12, f"Avatar en x negativo con bx={bx}: sx={sx}"

    def test_camera_is_visible_matches_screen_pos(self):
        from interface.camera import Camera

        cam = Camera(viewport_cells=8)
        cam.update((8, 8), grid_size=16)
        mn_x, mn_y, mx_x, mx_y = cam.get_visible_bounds()
        # Celdas dentro del viewport deben tener coordenadas de pantalla dentro del área
        for wx in range(mn_x, mx_x):
            sx, _ = cam.world_to_screen(wx, mn_y, cell_size=58, origin_x=0, origin_y=0)
            assert 0 <= sx < 8 * 58, f"wx={wx} visible pero sx={sx} fuera del viewport"
        # Celdas fuera del viewport tienen coordenadas fuera
        for wx in range(0, mn_x):
            sx, _ = cam.world_to_screen(wx, mn_y, cell_size=58, origin_x=0, origin_y=0)
            assert sx < 0, f"wx={wx} no visible pero sx={sx} >= 0"


class TestVersionConsistency:
    """Verifica que APP_VERSION es coherente en config, main y README."""

    def test_app_version_exists_in_config(self):
        from config import APP_VERSION

        assert isinstance(APP_VERSION, str)
        assert len(APP_VERSION) > 0

    def test_app_version_format(self):
        from config import APP_VERSION

        parts = APP_VERSION.split(".")
        assert len(parts) >= 2
        assert all(p.isdigit() for p in parts[:2])

    def test_main_imports_app_version(self):
        src = Path("main.py").read_text(encoding="utf-8")
        assert "APP_VERSION" in src

    def test_main_uses_version_in_title(self):
        src = Path("main.py").read_text(encoding="utf-8")
        assert "APP_VERSION" in src and "PygameView" in src

    def test_readme_mentions_version(self):
        from config import APP_VERSION

        readme = Path("README.md").read_text(encoding="utf-8")
        major_minor = ".".join(APP_VERSION.split(".")[:2])
        assert major_minor in readme

    def test_pygame_view_default_title_uses_version(self):
        src = Path("interface/pygame_view.py").read_text(encoding="utf-8")
        assert "APP_VERSION" in src
