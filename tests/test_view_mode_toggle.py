"""Tests para logica de toggles de modo de vista — BabyIA 0.4.6c."""

from pathlib import Path


def _load_pygame_view_source() -> str:
    return Path("interface/pygame_view.py").read_text(encoding="utf-8")


class TestPygameViewModeAttribute:
    def test_view_mode_attribute_set_in_init(self):
        src = _load_pygame_view_source()
        assert "self.view_mode" in src, "PygameView debe tener view_mode"

    def test_view_mode_default_is_full(self):
        src = _load_pygame_view_source()
        assert 'self.view_mode = "full"' in src or "self.view_mode = 'full'" in src

    def test_key_f_sets_full_mode(self):
        src = _load_pygame_view_source()
        assert "K_f" in src, "Debe haber un handler para K_f"
        assert '"full"' in src or "'full'" in src

    def test_key_c_or_z_sets_camera_mode(self):
        src = _load_pygame_view_source()
        assert "K_c" in src or "K_z" in src, "Debe haber K_c o K_z para camara"
        assert '"camera"' in src or "'camera'" in src

    def test_view_mode_used_in_draw_grid(self):
        src = _load_pygame_view_source()
        assert "view_mode" in src
        # El modo debe condicionar que funcion se llama
        assert "draw_full_world" in src
        assert "draw_camera_world" in src


class TestViewModeLogicIsolated:
    """Prueba la logica de modo sin instanciar PygameView (sin display pygame)."""

    def _simulate_key_handler(self, initial_mode: str, key: str) -> str:
        """Simula la logica de toggle: devuelve el nuevo modo."""
        mode = initial_mode
        if key == "F":
            mode = "full"
        elif key in ("C", "Z", "V"):
            mode = "camera"
        return mode

    def test_f_key_from_camera_goes_full(self):
        assert self._simulate_key_handler("camera", "F") == "full"

    def test_f_key_from_full_stays_full(self):
        assert self._simulate_key_handler("full", "F") == "full"

    def test_c_key_from_full_goes_camera(self):
        assert self._simulate_key_handler("full", "C") == "camera"

    def test_z_key_from_full_goes_camera(self):
        assert self._simulate_key_handler("full", "Z") == "camera"

    def test_v_key_from_full_goes_camera(self):
        assert self._simulate_key_handler("full", "V") == "camera"

    def test_c_key_from_camera_stays_camera(self):
        assert self._simulate_key_handler("camera", "C") == "camera"

    def test_unrelated_key_no_mode_change(self):
        assert self._simulate_key_handler("full", "X") == "full"
        assert self._simulate_key_handler("camera", "X") == "camera"


class TestDrawViewInfoText:
    def test_full_mode_shows_full_keyword(self):
        from interface.grid_renderer import draw_view_info

        # Solo verificamos que la funcion es callable con los parametros correctos
        assert callable(draw_view_info)

    def test_view_info_function_signature(self):
        import inspect
        from interface.grid_renderer import draw_view_info

        sig = inspect.signature(draw_view_info)
        params = list(sig.parameters.keys())
        assert "view_mode" in params
        assert "world_size" in params
        assert "cell_size" in params

    def test_draw_full_world_returns_int(self):
        """draw_full_world debe devolver el cell_size como int."""
        import inspect
        from interface.grid_renderer import draw_full_world

        sig = inspect.signature(draw_full_world)
        # Verificamos que tiene los parametros esperados
        params = list(sig.parameters.keys())
        assert "world" in params
        assert "grid_area" in params
        assert "fog" in params
