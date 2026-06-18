"""Tests de consistencia de version — BabyIA 0.4.6b."""

import pytest
from config import APP_VERSION
from brain.baby_brain import STATE_SIZE
from world.objects import STATE_SIZE as OBJECTS_STATE_SIZE


def test_app_version_is_046_or_later():
    assert APP_VERSION >= "0.4.6", f"APP_VERSION={APP_VERSION!r} debe ser >= 0.4.6"


def test_state_size_brain_is_40():
    assert (
        STATE_SIZE == 40
    ), f"brain/baby_brain.py STATE_SIZE={STATE_SIZE} (esperado 40)"


def test_state_size_objects_is_40():
    assert (
        OBJECTS_STATE_SIZE == 40
    ), f"world/objects.py STATE_SIZE={OBJECTS_STATE_SIZE} (esperado 40)"


def test_state_size_consistent_across_modules():
    assert (
        STATE_SIZE == OBJECTS_STATE_SIZE
    ), f"STATE_SIZE inconsistente: baby_brain={STATE_SIZE}, objects={OBJECTS_STATE_SIZE}"


def test_readme_mentions_046():
    from pathlib import Path

    readme = Path("README.md")
    if readme.exists():
        content = readme.read_text(encoding="utf-8")
        assert "0.4.6" in content, "README.md no menciona version 0.4.6"
    else:
        pytest.skip("README.md no encontrado")


def test_path_diagnostics_module_importable():
    from world.path_diagnostics import check_path_to_key_and_door

    assert callable(check_path_to_key_and_door)


def test_visual_memory_has_stagnation_api():
    from brain.visual_memory import VisualMemory

    vm = VisualMemory()
    assert hasattr(vm, "register_collision")
    assert hasattr(vm, "register_hazard")
    assert hasattr(vm, "register_visit")
    assert hasattr(vm, "repeated_collision_count")
    assert hasattr(vm, "repeated_hazard_count")
    assert hasattr(vm, "stuck_zone_hint")


def test_mission_reward_has_cap():
    from brain.mission_reward import MAX_MISSION_REWARD_PER_EPISODE

    assert MAX_MISSION_REWARD_PER_EPISODE > 0
