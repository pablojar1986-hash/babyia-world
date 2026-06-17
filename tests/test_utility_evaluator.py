"""Tests de brain/utility_evaluator.py."""
import pytest
from brain.utility_evaluator import UtilityEvaluator


@pytest.fixture
def ue():
    return UtilityEvaluator()


def test_basic_formula(ue):
    u = ue.evaluate(
        expected_reward=5.0,
        usefulness_for_goal=1.0,
        return_home_bonus=2.0,
        expected_risk=1.0,
        energy_cost=0.5,
        time_cost=0.3,
    )
    expected = 5.0 + 1.0 + 2.0 - 1.0 - 0.5 - 0.3
    assert u == pytest.approx(expected, abs=1e-4)


def test_last_utility_stored(ue):
    ue.evaluate(expected_reward=3.0)
    assert ue.last_utility == pytest.approx(3.0)


def test_last_breakdown_keys(ue):
    ue.evaluate(expected_reward=2.0, expected_risk=0.5)
    bd = ue.last_breakdown
    for key in ["expected_reward", "expected_risk", "total"]:
        assert key in bd


def test_all_costs_negative_effect(ue):
    u_no_cost = ue.evaluate(expected_reward=5.0, expected_risk=0.0, energy_cost=0.0, time_cost=0.0)
    u_with_cost = ue.evaluate(expected_reward=5.0, expected_risk=1.0, energy_cost=0.5, time_cost=0.2)
    assert u_no_cost > u_with_cost


def test_record_and_average_episode_utility(ue):
    ue.record_step_utility(2.0)
    ue.record_step_utility(4.0)
    assert ue.average_episode_utility() == pytest.approx(3.0)


def test_reset_episode_clears(ue):
    ue.record_step_utility(5.0)
    ue.reset_episode()
    assert ue.average_episode_utility() == pytest.approx(0.0)
    assert ue.last_utility == pytest.approx(0.0)


def test_zero_utility_when_all_zero(ue):
    u = ue.evaluate()
    assert u == pytest.approx(0.0)


def test_negative_utility_possible(ue):
    u = ue.evaluate(expected_risk=10.0)
    assert u < 0.0


def test_to_dict_keys(ue):
    ue.evaluate(expected_reward=1.0)
    d = ue.to_dict()
    for k in ["last_utility", "avg_episode_utility", "steps_evaluated", "last_breakdown"]:
        assert k in d
