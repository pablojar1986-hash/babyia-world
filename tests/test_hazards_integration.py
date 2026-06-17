"""Tests de integracion de hazards: apply_hazard_to_body + Inventory."""

import pytest
from brain.body_state import BodyState
from world.inventory import Inventory
from world.hazards import apply_hazard_to_body, is_blocked_by_body, HAZARD_TYPES


def _fresh():
    return BodyState(), Inventory()


def test_fire_zone_damages_without_immunity():
    bs, inv = _fresh()
    reward, blocked = apply_hazard_to_body("fire_zone", bs)
    assert not blocked
    assert reward == pytest.approx(-5.0)


def test_fire_zone_blocked_with_fire_immunity():
    bs, inv = _fresh()
    bs.fire_immunity = True
    reward, blocked = apply_hazard_to_body("fire_zone", bs)
    assert blocked
    assert reward == pytest.approx(0.0)


def test_spikes_blocked_by_shield():
    bs, inv = _fresh()
    bs.shield = 0.5
    reward, blocked = apply_hazard_to_body("spikes", bs)
    assert blocked
    assert reward == pytest.approx(0.0)


def test_spikes_damage_without_shield():
    bs, inv = _fresh()
    reward, blocked = apply_hazard_to_body("spikes", bs)
    assert not blocked
    assert reward == pytest.approx(-3.0)


def test_mud_not_blockable():
    bs, inv = _fresh()
    assert not is_blocked_by_body("mud", bs)
    speed_before = bs.speed
    reward, blocked = apply_hazard_to_body("mud", bs)
    assert not blocked
    assert bs.speed < speed_before


def test_take_damage_by_reduces_inventory_energy():
    _, inv = _fresh()
    inv.energy = 0.8
    lost = inv.take_damage_by(0.3)
    assert lost == pytest.approx(0.3)
    assert inv.energy == pytest.approx(0.5)


def test_take_damage_by_clamps_at_zero():
    _, inv = _fresh()
    inv.energy = 0.1
    lost = inv.take_damage_by(0.5)
    assert lost == pytest.approx(0.1)
    assert inv.energy == pytest.approx(0.0)


def test_three_grid_hazards_in_types():
    for hid in ("fire_zone", "spikes", "mud"):
        assert hid in HAZARD_TYPES, f"{hid} falta en HAZARD_TYPES"


def test_unknown_hazard_returns_zero():
    bs, _ = _fresh()
    reward, blocked = apply_hazard_to_body("nonexistent_hz", bs)
    assert reward == pytest.approx(0.0)
    assert not blocked
