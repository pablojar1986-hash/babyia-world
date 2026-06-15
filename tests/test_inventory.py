"""Tests de Inventory (world/inventory.py)."""
from world.inventory import Inventory, ENERGY_START, ENERGY_COST_DANGER, ENERGY_GAIN_FOOD, MAX_ENERGY


def test_initial_state():
    inv = Inventory()
    assert inv.has_key is False
    assert inv.energy == ENERGY_START
    assert inv.food_count == 0
    assert inv.touched_objects == []


def test_reset_clears_all():
    inv = Inventory()
    inv.pick_key()
    inv.eat_food()
    inv.reset()
    assert inv.has_key is False
    assert inv.energy == ENERGY_START
    assert inv.food_count == 0
    assert inv.touched_objects == []


def test_pick_key():
    inv = Inventory()
    inv.pick_key()
    assert inv.has_key is True
    assert "key" in inv.touched_objects


def test_use_key_removes_key():
    inv = Inventory()
    inv.pick_key()
    inv.use_key()
    assert inv.has_key is False


def test_eat_food_increases_energy():
    inv = Inventory()
    inv.energy = 0.5
    inv.eat_food()
    assert inv.energy > 0.5
    assert inv.food_count == 1
    assert "food" in inv.touched_objects


def test_eat_food_caps_at_max():
    inv = Inventory()
    inv.energy = MAX_ENERGY
    inv.eat_food()
    assert inv.energy <= MAX_ENERGY


def test_take_damage_reduces_energy():
    inv = Inventory()
    inv.take_damage()
    assert inv.energy < ENERGY_START
    assert inv.energy >= 0.0


def test_take_damage_does_not_go_negative():
    inv = Inventory()
    inv.energy = 0.0
    inv.take_damage()
    assert inv.energy == 0.0


def test_first_touch_detection():
    inv = Inventory()
    assert inv.first_touch("key") is True
    inv.pick_key()
    assert inv.first_touch("key") is False


def test_touch_registers_object():
    inv = Inventory()
    inv.touch("unknown")
    assert "unknown" in inv.touched_objects


def test_to_dict_structure():
    inv = Inventory()
    d = inv.to_dict()
    assert "has_key" in d
    assert "energy" in d
    assert "food_count" in d
    assert "touched" in d


def test_eat_food_returns_gain():
    inv = Inventory()
    inv.energy = 0.5
    gain = inv.eat_food()
    assert gain > 0.0


def test_take_damage_returns_lost():
    inv = Inventory()
    lost = inv.take_damage()
    assert lost == ENERGY_COST_DANGER
