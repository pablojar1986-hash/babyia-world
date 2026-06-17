"""Tests de UtilityEvaluator.evaluate_from_context con inventario real."""

import pytest
from brain.body_state import BodyState
from brain.utility_evaluator import UtilityEvaluator
from world.inventory import Inventory


class _FakeCausal:
    def count_learned(self):
        return 0


class _FakeWorld:
    current_world = "home"

    def should_return_home(self):
        return False


def _eval(energy=1.0, base_reward=0.0, step_count=0, causal=None):
    bs = BodyState()
    inv = Inventory()
    inv.energy = energy
    evaluator = UtilityEvaluator()
    return evaluator.evaluate_from_context(
        bs,
        _FakeWorld(),
        causal or _FakeCausal(),
        base_reward=base_reward,
        step_count=step_count,
        inventory=inv,
    )


def test_full_energy_has_zero_energy_cost():
    ue = UtilityEvaluator()
    bs = BodyState()
    inv = Inventory()
    inv.energy = 1.0
    ue.evaluate_from_context(bs, _FakeWorld(), _FakeCausal(), inventory=inv)
    bd = ue.last_breakdown
    assert bd["energy_cost"] == pytest.approx(0.0)


def test_empty_energy_has_max_energy_cost():
    ue = UtilityEvaluator()
    bs = BodyState()
    inv = Inventory()
    inv.energy = 0.0
    ue.evaluate_from_context(bs, _FakeWorld(), _FakeCausal(), inventory=inv)
    bd = ue.last_breakdown
    assert bd["energy_cost"] == pytest.approx(0.5)


def test_inventory_none_defaults_to_full_energy():
    ue = UtilityEvaluator()
    bs = BodyState()
    ue.evaluate_from_context(bs, _FakeWorld(), _FakeCausal(), inventory=None)
    bd = ue.last_breakdown
    assert bd["energy_cost"] == pytest.approx(0.0)


def test_shield_does_not_affect_energy_cost():
    ue1, ue2 = UtilityEvaluator(), UtilityEvaluator()
    bs1, bs2 = BodyState(), BodyState()
    inv = Inventory()
    inv.energy = 0.5
    bs1.shield = 0.0
    bs2.shield = 0.9
    ue1.evaluate_from_context(bs1, _FakeWorld(), _FakeCausal(), inventory=inv)
    ue2.evaluate_from_context(bs2, _FakeWorld(), _FakeCausal(), inventory=inv)
    assert ue1.last_breakdown["energy_cost"] == pytest.approx(
        ue2.last_breakdown["energy_cost"]
    )


def test_time_cost_grows_with_steps():
    ue1, ue2 = UtilityEvaluator(), UtilityEvaluator()
    bs = BodyState()
    inv = Inventory()
    ue1.evaluate_from_context(
        bs, _FakeWorld(), _FakeCausal(), step_count=0, inventory=inv
    )
    ue2.evaluate_from_context(
        bs, _FakeWorld(), _FakeCausal(), step_count=100, inventory=inv
    )
    assert ue2.last_breakdown["time_cost"] > ue1.last_breakdown["time_cost"]


def test_returns_float():
    result = _eval()
    assert isinstance(result, float)
