"""Tests de integracion de powerups: apply_powerup_effect + Inventory + BodyState."""

import pytest
from brain.body_state import BodyState
from world.inventory import Inventory
from world.powerups import apply_powerup_effect, POWERUP_TYPES


def _fresh():
    return BodyState(), Inventory()


def test_energy_food_restores_inventory_energy():
    bs, inv = _fresh()
    inv.energy = 0.4
    reward = apply_powerup_effect("energy_food", bs, inv)
    assert inv.energy == pytest.approx(0.9)
    assert reward == pytest.approx(3.0)


def test_energy_food_does_not_exceed_max():
    bs, inv = _fresh()
    inv.energy = 0.8
    apply_powerup_effect("energy_food", bs, inv)
    assert inv.energy <= 1.0


def test_energy_food_does_not_change_body_state():
    bs, inv = _fresh()
    size_before = bs.size
    apply_powerup_effect("energy_food", bs, inv)
    assert bs.size == pytest.approx(size_before)


def test_growth_crystal_increases_size_not_energy():
    bs, inv = _fresh()
    energy_before = inv.energy
    apply_powerup_effect("growth_crystal", bs, inv)
    assert bs.size == pytest.approx(1.5)
    assert inv.energy == pytest.approx(energy_before)


def test_shield_orb_adds_shield():
    bs, inv = _fresh()
    apply_powerup_effect("shield_orb", bs, inv)
    assert bs.shield == pytest.approx(0.5)


def test_speed_boots_increases_speed():
    bs, inv = _fresh()
    apply_powerup_effect("speed_boots", bs, inv)
    assert bs.speed == pytest.approx(1.5)


def test_unknown_powerup_returns_zero():
    bs, inv = _fresh()
    reward = apply_powerup_effect("nonexistent_pu", bs, inv)
    assert reward == pytest.approx(0.0)


def test_all_four_grid_powerups_in_types():
    for pid in ("growth_crystal", "shield_orb", "energy_food", "speed_boots"):
        assert pid in POWERUP_TYPES, f"{pid} falta en POWERUP_TYPES"


def test_restore_energy_clamps_at_1():
    inv = Inventory()
    inv.energy = 1.0
    gain = inv.restore_energy(0.5)
    assert gain == pytest.approx(0.0)
    assert inv.energy == pytest.approx(1.0)


def test_restore_energy_partial():
    inv = Inventory()
    inv.energy = 0.6
    gain = inv.restore_energy(0.5)
    assert gain == pytest.approx(0.4)
    assert inv.energy == pytest.approx(1.0)
