"""Tests de brain/body_state.py — estado corporal de BabyIA."""
import numpy as np
import pytest
from brain.body_state import BodyState, MAX_SIZE, MAX_SPEED, MIN_SIZE, MIN_SPEED


def make():
    return BodyState()


def test_initial_values():
    bs = make()
    assert bs.size            == 1.0
    assert bs.speed           == 1.0
    assert bs.shield          == 0.0
    assert bs.fire_immunity   is False
    assert bs.poison_immunity is False
    assert bs.vision_range    == 3
    assert bs.memory_focus    == 1.0


def test_apply_powerup_increase_size():
    bs = make()
    bs.apply_powerup("g", "increase_size", 0.5)
    assert bs.size == pytest.approx(1.5)


def test_apply_powerup_max_size_clamped():
    bs = make()
    bs.apply_powerup("g", "increase_size", 10.0)
    assert bs.size == MAX_SIZE


def test_apply_powerup_increase_speed():
    bs = make()
    bs.apply_powerup("s", "increase_speed", 0.5)
    assert bs.speed == pytest.approx(1.5)


def test_apply_powerup_fire_immunity():
    bs = make()
    bs.apply_powerup("f", "fire_immunity", 1.0)
    assert bs.fire_immunity is True


def test_apply_powerup_shield():
    bs = make()
    bs.apply_powerup("sh", "add_shield", 0.5)
    assert bs.shield == pytest.approx(0.5)


def test_apply_hazard_reduce_speed_blocked():
    bs = make()
    result = bs.apply_hazard("mud", "reduce_speed", 0.3, blocked=True)
    assert result == 0.0
    assert bs.speed == 1.0  # no cambio


def test_apply_hazard_reduce_speed_not_blocked():
    bs = make()
    bs.apply_hazard("mud", "reduce_speed", 0.3, blocked=False)
    assert bs.speed == pytest.approx(1.0 - 0.3)


def test_apply_hazard_min_speed_clamped():
    bs = make()
    bs.apply_hazard("x", "reduce_speed", 5.0, blocked=False)
    assert bs.speed == MIN_SPEED


def test_apply_hazard_energy_damage_returns_value():
    bs = make()
    dmg = bs.apply_hazard("fire", "energy_damage", 0.3, blocked=False)
    assert dmg == pytest.approx(0.3)


def test_is_protected_fire():
    bs = make()
    bs.fire_immunity = True
    assert bs.is_protected_against("fire") is True
    assert bs.is_protected_against("poison") is False


def test_is_protected_spikes_with_shield():
    bs = make()
    bs.shield = 0.5
    assert bs.is_protected_against("spikes") is True


def test_tick_effects_shield_decay():
    bs = make()
    bs.shield = 0.5
    bs.tick_effects()
    assert bs.shield < 0.5


def test_tick_effects_expires_temporal_powerup():
    bs = make()
    bs.apply_powerup("sb", "increase_speed", 0.5, duration=2)
    assert bs.speed == pytest.approx(1.5)
    bs.tick_effects()  # remaining=1
    bs.tick_effects()  # remaining=0 → revierte
    assert bs.speed == pytest.approx(1.0)


def test_reset_for_episode():
    bs = make()
    bs.size = 2.0
    bs.fire_immunity = True
    bs.shield = 0.8
    bs.reset_for_episode()
    assert bs.size          == 1.0
    assert bs.fire_immunity is False
    assert bs.shield        == 0.0


def test_get_state_features_length():
    bs = make()
    feats = bs.get_state_features()
    assert feats.shape == (8,)
    assert feats.dtype == np.float32


def test_get_state_features_normalizado():
    bs = make()
    bs.size  = MAX_SIZE
    bs.speed = MAX_SPEED
    feats = bs.get_state_features()
    assert feats[0] == pytest.approx(1.0)   # size normalizado
    assert feats[1] == pytest.approx(1.0)   # speed normalizado


def test_to_dict_contains_keys():
    bs = make()
    d = bs.to_dict()
    for key in ["size", "speed", "shield", "fire_immunity", "poison_immunity",
                "vision_range", "memory_focus", "active_effects"]:
        assert key in d
