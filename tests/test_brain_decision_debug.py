"""Tests de last_decision en BabyBrain — diagnóstico de exploración/explotación."""

import numpy as np
import pytest
from brain.baby_brain import BabyBrain, STATE_SIZE


@pytest.fixture
def brain():
    return BabyBrain()


@pytest.fixture
def state():
    return np.zeros(STATE_SIZE, dtype=np.float32)


def test_last_decision_initialized(brain):
    assert "action" in brain.last_decision
    assert "decision_type" in brain.last_decision
    assert "effective_epsilon" in brain.last_decision
    assert "q_values" in brain.last_decision


def test_exploration_when_epsilon_one(brain, state):
    brain.epsilon = 1.0
    brain.select_action(state)
    assert brain.last_decision["decision_type"] == "exploration"


def test_exploitation_when_epsilon_zero(brain, state):
    brain.epsilon = 0.0
    brain.select_action(state)
    assert brain.last_decision["decision_type"] == "exploitation"


def test_exploitation_stores_q_values(brain, state):
    brain.epsilon = 0.0
    brain.select_action(state)
    assert len(brain.last_decision["q_values"]) == 5


def test_exploration_q_values_empty(brain, state):
    brain.epsilon = 1.0
    brain.select_action(state)
    assert brain.last_decision["q_values"] == []


def test_effective_epsilon_stored(brain, state):
    brain.epsilon = 0.5
    brain.select_action(state, extra_exploration=0.1)
    assert brain.last_decision["effective_epsilon"] == pytest.approx(0.6, abs=1e-4)


def test_effective_epsilon_clamped_at_one(brain, state):
    brain.epsilon = 1.0
    brain.select_action(state, extra_exploration=0.5)
    assert brain.last_decision["effective_epsilon"] == pytest.approx(1.0)


def test_action_matches_return_value(brain, state):
    brain.epsilon = 0.0
    action = brain.select_action(state)
    assert brain.last_decision["action"] == action


def test_action_valid_range(brain, state):
    for _ in range(20):
        action = brain.select_action(state)
        assert 0 <= action < 5


def test_decision_type_is_string(brain, state):
    brain.select_action(state)
    assert isinstance(brain.last_decision["decision_type"], str)
