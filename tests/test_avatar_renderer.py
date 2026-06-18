"""Tests de AvatarRenderer (logica, sin renderizado real)."""

from interface.avatar_renderer import AvatarRenderer, _LEVEL_COLORS


def test_renderer_instantiates():
    ar = AvatarRenderer()
    assert ar is not None
    assert ar._font_xs is None  # no inicializado hasta primer render


def test_level_colors_defined_for_all_levels():
    for lvl in range(8):
        assert lvl in _LEVEL_COLORS, f"Falta color para nivel {lvl}"
        c = _LEVEL_COLORS[lvl]
        assert len(c) == 3
        assert all(0 <= v <= 255 for v in c)


def test_tint_low_energy_darkens():
    base = (200, 200, 200)
    full = AvatarRenderer._tint(base, energy=1.0, curiosity=0.0)
    low = AvatarRenderer._tint(base, energy=0.0, curiosity=0.0)
    assert all(
        low[i] <= full[i] for i in range(3)
    ), "Energia baja debe oscurecer el avatar"


def test_tint_high_curiosity_adds_blue():
    base = (100, 100, 100)
    normal = AvatarRenderer._tint(base, energy=1.0, curiosity=0.0)
    curio = AvatarRenderer._tint(base, energy=1.0, curiosity=1.0)
    assert curio[2] >= normal[2], "Curiosidad alta debe agregar tono azul"


def test_tint_output_is_valid_rgb():
    base = (255, 255, 255)
    result = AvatarRenderer._tint(base, energy=0.5, curiosity=0.5)
    assert len(result) == 3
    assert all(0 <= v <= 255 for v in result)
