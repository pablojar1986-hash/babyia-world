"""Tests de version para BabyIA 0.4.7."""

import pytest
from config import APP_VERSION
from brain.baby_brain import STATE_SIZE
from world.objects import STATE_SIZE as OBJECTS_STATE_SIZE


def test_app_version_is_047():
    assert APP_VERSION.startswith(
        "0.4.7"
    ), f"APP_VERSION={APP_VERSION!r} no empieza por 0.4.7"


def test_state_size_is_40():
    assert (
        STATE_SIZE == 40
    ), f"brain/baby_brain.py STATE_SIZE={STATE_SIZE} (esperado 40)"


def test_objects_state_size_is_40():
    assert (
        OBJECTS_STATE_SIZE == 40
    ), f"world/objects.py STATE_SIZE={OBJECTS_STATE_SIZE} (esperado 40)"


def test_state_size_synchronized():
    assert (
        STATE_SIZE == OBJECTS_STATE_SIZE
    ), f"STATE_SIZE desincronizado: baby_brain={STATE_SIZE}, objects={OBJECTS_STATE_SIZE}"


def test_readme_mentions_047():
    from pathlib import Path

    readme = Path("README.md")
    if readme.exists():
        assert "0.4.7" in readme.read_text(
            encoding="utf-8"
        ), "README.md no menciona 0.4.7"
    else:
        pytest.skip("README.md no encontrado")


def test_evolucion_mentions_047():
    from pathlib import Path

    evo = Path("docs/evolucion.md")
    if evo.exists():
        assert "0.4.7" in evo.read_text(
            encoding="utf-8"
        ), "docs/evolucion.md no menciona 0.4.7"
    else:
        pytest.skip("docs/evolucion.md no encontrado")


def test_network_inspector_version_is_046():
    from pathlib import Path

    ni = Path("brain/network_inspector.py")
    if ni.exists():
        text = ni.read_text(encoding="utf-8")
        assert "0.4.6" in text, "network_inspector.py no menciona version 0.4.6"
    else:
        pytest.skip("brain/network_inspector.py no encontrado")
