"""Tests de estructura para interface/grid_renderer.py — BabyIA 0.4.6c."""

import types
import importlib


def test_grid_renderer_importable():
    mod = importlib.import_module("interface.grid_renderer")
    assert isinstance(mod, types.ModuleType)


def test_has_draw_full_world():
    from interface.grid_renderer import draw_full_world

    assert callable(draw_full_world)


def test_has_draw_camera_world():
    from interface.grid_renderer import draw_camera_world

    assert callable(draw_camera_world)


def test_has_draw_view_info():
    from interface.grid_renderer import draw_view_info

    assert callable(draw_view_info)


def test_cell_colors_dict_present():
    from interface.grid_renderer import CELL_COLORS

    assert isinstance(CELL_COLORS, dict)
    assert len(CELL_COLORS) >= 10


def test_cell_labels_dict_present():
    from interface.grid_renderer import CELL_LABELS

    assert isinstance(CELL_LABELS, dict)
    assert len(CELL_LABELS) >= 10


def test_portal_colors_dict_present():
    from interface.grid_renderer import PORTAL_COLORS

    assert isinstance(PORTAL_COLORS, dict)
    assert len(PORTAL_COLORS) >= 3


def test_cell_colors_keys_are_ints():
    from interface.grid_renderer import CELL_COLORS

    for k in CELL_COLORS:
        assert isinstance(k, int), f"Clave {k!r} no es int"


def test_cell_colors_values_are_rgb_tuples():
    from interface.grid_renderer import CELL_COLORS

    for k, v in CELL_COLORS.items():
        assert isinstance(v, tuple) and len(v) == 3, f"Color {v!r} no es RGB"
        for ch in v:
            assert 0 <= ch <= 255, f"Canal {ch} fuera de rango"


def test_no_pygame_required_for_color_dicts():
    """Las constantes de color deben ser accesibles sin display de pygame."""
    from interface.grid_renderer import CELL_COLORS, CELL_LABELS, PORTAL_COLORS

    assert CELL_COLORS is not None
    assert CELL_LABELS is not None
    assert PORTAL_COLORS is not None


def test_pygame_view_imports_from_grid_renderer():
    """pygame_view debe importar colores desde grid_renderer, no definirlos."""
    import ast
    from pathlib import Path

    src = Path("interface/pygame_view.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imports_from_renderer = any(
        isinstance(node, ast.ImportFrom) and node.module == "interface.grid_renderer"
        for node in ast.walk(tree)
    )
    assert (
        imports_from_renderer
    ), "pygame_view.py debe importar de interface.grid_renderer"


def test_grid_renderer_under_300_lines():
    from pathlib import Path

    lines = Path("interface/grid_renderer.py").read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 300, f"grid_renderer.py tiene {len(lines)} lineas (max 300)"
