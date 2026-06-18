"""Tests de world/powerups.py."""

import pytest
from brain.body_state import BodyState
from world.powerups import POWERUP_TYPES, PowerupDef, apply_powerup_to_body


def test_all_powerup_ids_present():
    expected = {
        "growth_crystal",
        "speed_boots",
        "shield_orb",
        "fire_immunity",
        "poison_immunity",
        "vision_light",
        "memory_crystal",
        "energy_food",
    }
    assert set(POWERUP_TYPES.keys()) == expected


def test_each_powerup_is_powerupdef():
    for pu in POWERUP_TYPES.values():
        assert isinstance(pu, PowerupDef)


def test_growth_crystal_increases_size():
    bs = BodyState()
    reward = apply_powerup_to_body("growth_crystal", bs)
    assert bs.size == pytest.approx(1.5)
    assert reward == pytest.approx(3.0)


def test_fire_immunity_sets_flag():
    bs = BodyState()
    apply_powerup_to_body("fire_immunity", bs)
    assert bs.fire_immunity is True


def test_poison_immunity_sets_flag():
    bs = BodyState()
    apply_powerup_to_body("poison_immunity", bs)
    assert bs.poison_immunity is True


def test_speed_boots_increases_speed():
    bs = BodyState()
    apply_powerup_to_body("speed_boots", bs)
    assert bs.speed == pytest.approx(1.5)


def test_shield_orb_adds_shield():
    bs = BodyState()
    apply_powerup_to_body("shield_orb", bs)
    assert bs.shield == pytest.approx(0.5)


def test_unknown_powerup_returns_zero():
    bs = BodyState()
    reward = apply_powerup_to_body("nonexistent_powerup", bs)
    assert reward == 0.0


def test_concept_signal_contains_cause():
    pu = POWERUP_TYPES["growth_crystal"]
    sig = pu.get_concept_signal()
    assert sig["cause"] == "growth_crystal"
    assert "effect" in sig
    assert "useful_for" in sig


def test_all_powerups_have_positive_reward():
    for pu in POWERUP_TYPES.values():
        assert pu.reward_delta > 0.0
