"""Tests de world/doors.py — requisitos de puertas."""

from brain.body_state import BodyState
from world.doors import DOOR_TYPES, DoorRequirement, attempt_door


def test_all_door_ids_present():
    expected = {
        "heavy_door",
        "speed_door",
        "fire_door",
        "poison_door",
        "small_door",
        "memory_door",
    }
    assert set(DOOR_TYPES.keys()) == expected


def test_each_door_is_doorrequirement():
    for d in DOOR_TYPES.values():
        assert isinstance(d, DoorRequirement)


def test_heavy_door_fails_small_baby():
    bs = BodyState()  # size=1.0 < 1.5
    result = attempt_door("heavy_door", bs)
    assert result["success"] is False
    assert result["reward_delta"] < 0.0


def test_heavy_door_passes_big_baby():
    bs = BodyState()
    bs.size = 1.5
    result = attempt_door("heavy_door", bs)
    assert result["success"] is True
    assert result["reward_delta"] > 0.0


def test_speed_door_fails_slow_baby():
    bs = BodyState()  # speed=1.0 < 1.5
    result = attempt_door("speed_door", bs)
    assert result["success"] is False


def test_speed_door_passes_fast_baby():
    bs = BodyState()
    bs.speed = 1.5
    result = attempt_door("speed_door", bs)
    assert result["success"] is True


def test_fire_door_fails_without_fire_immunity():
    bs = BodyState()
    result = attempt_door("fire_door", bs)
    assert result["success"] is False


def test_fire_door_passes_with_fire_immunity():
    bs = BodyState()
    bs.fire_immunity = True
    result = attempt_door("fire_door", bs)
    assert result["success"] is True


def test_poison_door_fails_without_poison_immunity():
    bs = BodyState()
    result = attempt_door("poison_door", bs)
    assert result["success"] is False


def test_poison_door_passes_with_poison_immunity():
    bs = BodyState()
    bs.poison_immunity = True
    result = attempt_door("poison_door", bs)
    assert result["success"] is True


def test_unknown_door_returns_fail():
    bs = BodyState()
    result = attempt_door("nonexistent_door", bs)
    assert result["success"] is False
    assert "desconocida" in result["fail_reason"]


def test_small_door_passes_default_size():
    bs = BodyState()  # size=1.0
    result = attempt_door("small_door", bs)
    assert result["success"] is True


def test_fail_reason_mentions_size():
    bs = BodyState()  # size=1.0
    door = DOOR_TYPES["heavy_door"]
    reason = door.get_fail_reason(bs)
    assert "tamano" in reason


def test_to_dict_has_required_keys():
    d = DOOR_TYPES["heavy_door"].to_dict()
    assert "door_id" in d and "required_size" in d
