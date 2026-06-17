"""Tests de brain/neural_debugger.py — inspección diagnóstica del DQN."""

import numpy as np
import pytest
from brain.baby_brain import BabyBrain, STATE_SIZE, ACTION_SIZE
from brain.neural_debugger import (
    get_q_values,
    get_action_ranking,
    get_layer_activation_summary,
    get_brain_snapshot,
)

_ACTION_NAMES = ["arriba", "abajo", "izquierda", "derecha", "esperar"]


@pytest.fixture
def brain():
    return BabyBrain()


@pytest.fixture
def state():
    return np.zeros(STATE_SIZE, dtype=np.float32)


def test_get_q_values_returns_five_actions(brain, state):
    qv = get_q_values(brain, state)
    assert len(qv) == 5


def test_get_q_values_keys_match_action_names(brain, state):
    qv = get_q_values(brain, state)
    assert set(qv.keys()) == set(_ACTION_NAMES)


def test_get_q_values_all_float(brain, state):
    qv = get_q_values(brain, state)
    for v in qv.values():
        assert isinstance(v, float)


def test_get_q_values_does_not_modify_epsilon(brain, state):
    eps_before = brain.epsilon
    get_q_values(brain, state)
    assert brain.epsilon == eps_before


def test_get_q_values_does_not_modify_buffer(brain, state):
    buf_before = len(brain.buffer)
    get_q_values(brain, state)
    assert len(brain.buffer) == buf_before


def test_get_action_ranking_length(brain, state):
    ranking = get_action_ranking(brain, state)
    assert len(ranking) == 5


def test_get_action_ranking_sorted(brain, state):
    ranking = get_action_ranking(brain, state)
    for i in range(len(ranking) - 1):
        assert ranking[i]["q_value"] >= ranking[i + 1]["q_value"]


def test_get_layer_activation_summary_structure(brain, state):
    layers = get_layer_activation_summary(brain, state)
    assert len(layers) == 4
    names = [la["name"] for la in layers]
    assert "input" in names
    assert "hidden_1" in names
    assert "hidden_2" in names
    assert "output" in names


def test_get_layer_activation_summary_sizes(brain, state):
    layers = get_layer_activation_summary(brain, state)
    sizes = {la["name"]: la["size"] for la in layers}
    assert sizes["input"] == STATE_SIZE
    assert sizes["hidden_1"] == 128
    assert sizes["hidden_2"] == 64
    assert sizes["output"] == ACTION_SIZE


def test_layer_activations_are_non_negative(brain, state):
    layers = get_layer_activation_summary(brain, state)
    for la in layers:
        if la["activation_mean"] is not None:
            assert la["activation_mean"] >= 0.0


def test_get_brain_snapshot_state_size(brain, state):
    snap = get_brain_snapshot(brain, state)
    assert snap["state_size"] == STATE_SIZE


def test_get_brain_snapshot_action_size(brain, state):
    snap = get_brain_snapshot(brain, state)
    assert snap["action_size"] == 5


def test_get_brain_snapshot_exploration_flag(brain, state):
    snap = get_brain_snapshot(brain, state, last_action=0, exploration=True)
    assert snap["decision_type"] == "exploration"


def test_get_brain_snapshot_exploitation_flag(brain, state):
    snap = get_brain_snapshot(brain, state, last_action=3, exploration=False)
    assert snap["decision_type"] == "exploitation"


def test_get_brain_snapshot_does_not_modify_weights(brain, state):
    w_before = brain.q_net.net[0].weight.data.clone()
    get_brain_snapshot(brain, state)
    w_after = brain.q_net.net[0].weight.data
    assert (w_before - w_after).abs().max().item() == pytest.approx(0.0)


def test_get_brain_snapshot_has_required_keys(brain, state):
    snap = get_brain_snapshot(brain, state)
    for key in [
        "epsilon",
        "last_action",
        "decision_type",
        "q_values",
        "best_action",
        "replay_buffer_size",
        "train_steps",
        "last_loss",
        "layers",
    ]:
        assert key in snap
