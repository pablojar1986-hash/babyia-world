"""Tests de brain/survival.py — SurvivalEvaluator."""

from brain.body_state import BodyState
from brain.survival import SurvivalEvaluator
from world.inventory import Inventory


class _FakeWorld:
    is_at_home = False


class _HomeWorld:
    is_at_home = True


def _eval(energy=1.0, shield=0.0, fire_imm=False, poison_imm=False, at_home=False):
    bs = BodyState()
    bs.shield = shield
    bs.fire_immunity = fire_imm
    bs.poison_immunity = poison_imm
    inv = Inventory()
    inv.energy = energy
    world = _HomeWorld() if at_home else _FakeWorld()
    return SurvivalEvaluator().evaluate(bs, inv, world)


def test_evaluate_returns_required_keys():
    result = _eval()
    for k in (
        "risk_level",
        "recommendation",
        "should_return_home",
        "needs_food",
        "danger_without_protection",
    ):
        assert k in result, f"Falta clave: {k}"


def test_full_energy_low_risk():
    result = _eval(energy=1.0)
    assert result["risk_level"] < 0.5
    assert not result["needs_food"]


def test_low_energy_triggers_needs_food():
    result = _eval(energy=0.2)
    assert result["needs_food"]


def test_low_energy_no_protection_is_dangerous():
    result = _eval(energy=0.2, shield=0.0)
    assert result["danger_without_protection"]


def test_shield_reduces_danger_without_protection():
    result = _eval(energy=0.4, shield=0.5)
    assert not result["danger_without_protection"]


def test_risk_level_bounded():
    for energy in (0.0, 0.3, 0.7, 1.0):
        result = _eval(energy=energy)
        assert 0.0 <= result["risk_level"] <= 1.0


def test_low_energy_away_from_home_recommends_return_or_food():
    result = _eval(energy=0.1, at_home=False)
    assert result["recommendation"] in (
        "buscar_comida_o_regresar",
        "evitar_peligros",
        "regresar_a_casa",
    )


def test_high_risk_is_reflected():
    result = _eval(energy=0.0, shield=0.0)
    assert result["risk_level"] >= 0.5


def test_recommendation_is_string():
    result = _eval()
    assert isinstance(result["recommendation"], str)
    assert len(result["recommendation"]) > 0
