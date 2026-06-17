"""Tests de integracion de puertas especiales: DoorRequirement + attempt_door."""

import pytest
from brain.body_state import BodyState
from world.doors import attempt_door, DOOR_TYPES, DoorRequirement


def _bs():
    return BodyState()


def test_heavy_door_fails_small_baby():
    bs = _bs()  # size=1.0 < 1.5
    result = attempt_door("heavy_door", bs)
    assert not result["success"]
    assert result["reward_delta"] == pytest.approx(-1.0)


def test_heavy_door_passes_large_baby():
    bs = _bs()
    bs.size = 1.5
    result = attempt_door("heavy_door", bs)
    assert result["success"]
    assert result["reward_delta"] == pytest.approx(8.0)


def test_small_door_passes_normal_size():
    bs = _bs()  # size=1.0 <= 1.2
    result = attempt_door("small_door", bs)
    assert result["success"]


def test_small_door_fails_after_growth():
    bs = _bs()
    bs.size = 1.5  # > max_size=1.2
    result = attempt_door("small_door", bs)
    assert not result["success"]
    assert "tamano excesivo" in result["fail_reason"]


def test_small_door_max_size_configured():
    sd = DOOR_TYPES.get("small_door")
    assert sd is not None
    assert sd.max_size == pytest.approx(1.2)


def test_fire_door_requires_immunity():
    bs = _bs()
    result = attempt_door("fire_door", bs)
    assert not result["success"]
    bs.fire_immunity = True
    result = attempt_door("fire_door", bs)
    assert result["success"]


def test_poison_door_requires_immunity():
    bs = _bs()
    result = attempt_door("poison_door", bs)
    assert not result["success"]
    bs.poison_immunity = True
    result = attempt_door("poison_door", bs)
    assert result["success"]


def test_both_grid_doors_in_types():
    for did in ("heavy_door", "small_door"):
        assert did in DOOR_TYPES, f"{did} falta en DOOR_TYPES"


def test_unknown_door_fails_gracefully():
    bs = _bs()
    result = attempt_door("no_such_door", bs)
    assert not result["success"]
    assert result["reward_delta"] == pytest.approx(0.0)


def test_door_can_pass_checks_max_size():
    dr = DoorRequirement(door_id="test", name="Test", required_size=0.0, max_size=1.0)
    bs = _bs()
    bs.size = 0.9
    assert dr.can_pass(bs)
    bs.size = 1.1
    assert not dr.can_pass(bs)
