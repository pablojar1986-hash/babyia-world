"""Tests de world/hazards.py."""

import pytest
from brain.body_state import BodyState
from world.hazards import (
    HAZARD_TYPES,
    HazardDef,
    apply_hazard_to_body,
    is_blocked_by_body,
)


def test_all_hazard_ids_present():
    expected = {
        "fire_zone",
        "poison_zone",
        "mud",
        "shrink_trap",
        "slow_trap",
        "darkness",
        "spikes",
        "energy_drain",
    }
    assert set(HAZARD_TYPES.keys()) == expected


def test_each_hazard_is_hazarddef():
    for hz in HAZARD_TYPES.values():
        assert isinstance(hz, HazardDef)


def test_fire_zone_blocked_by_fire_immunity():
    bs = BodyState()
    bs.fire_immunity = True
    blocked = is_blocked_by_body("fire_zone", bs)
    assert blocked is True


def test_fire_zone_not_blocked_without_immunity():
    bs = BodyState()
    blocked = is_blocked_by_body("fire_zone", bs)
    assert blocked is False


def test_spikes_blocked_by_shield():
    bs = BodyState()
    bs.shield = 0.5
    blocked = is_blocked_by_body("spikes", bs)
    assert blocked is True


def test_mud_not_blockable():
    bs = BodyState()
    bs.shield = 1.0
    bs.fire_immunity = True
    blocked = is_blocked_by_body("mud", bs)
    assert blocked is False


def test_apply_fire_zone_blocked_zero_reward():
    bs = BodyState()
    bs.fire_immunity = True
    reward, blocked = apply_hazard_to_body("fire_zone", bs)
    assert blocked is True
    assert reward == pytest.approx(0.0)


def test_apply_fire_zone_not_blocked_negative_reward():
    bs = BodyState()
    reward, blocked = apply_hazard_to_body("fire_zone", bs)
    assert blocked is False
    assert reward < 0.0


def test_apply_mud_reduces_speed():
    bs = BodyState()
    apply_hazard_to_body("mud", bs)
    assert bs.speed < 1.0


def test_all_hazards_have_negative_reward():
    for hz in HAZARD_TYPES.values():
        assert hz.reward_delta < 0.0


def test_concept_signal_contains_cause():
    hz = HAZARD_TYPES["fire_zone"]
    sig = hz.get_concept_signal()
    assert sig["cause"] == "fire_zone"
    assert "effect" in sig
    assert "countermeasure" in sig
