"""Tests del payload status que el Trainer envia a los paneles visuales (0.4.2)."""

import pytest
from brain.trainer import Trainer


@pytest.fixture(scope="module")
def status():
    t = Trainer(training=False)
    t.start_episode()
    return t.get_status()


def test_status_has_survival_key(status):
    assert "survival" in status


def test_status_survival_is_dict(status):
    assert isinstance(status["survival"], dict)


def test_status_survival_has_required_keys(status):
    sv = status["survival"]
    for k in (
        "risk_level",
        "recommendation",
        "should_return_home",
        "needs_food",
        "danger_without_protection",
    ):
        assert k in sv or sv == {}, f"Falta {k} en survival (puede ser vacio al inicio)"


def test_status_has_causal_relations(status):
    assert "causal_relations" in status
    assert isinstance(status["causal_relations"], list)


def test_status_has_ep_counters(status):
    for key in (
        "ep_powerups",
        "ep_hazards",
        "ep_hazards_blocked",
        "ep_door_attempts",
        "ep_door_successes",
    ):
        assert key in status, f"Falta {key} en status"


def test_ep_counters_start_at_zero(status):
    for key in (
        "ep_powerups",
        "ep_hazards",
        "ep_hazards_blocked",
        "ep_door_attempts",
        "ep_door_successes",
    ):
        assert status[key] == 0


def test_status_has_inventory(status):
    assert "inventory" in status
    inv = status["inventory"]
    assert "energy" in inv
    assert 0.0 <= inv["energy"] <= 1.0


def test_status_has_ep_events(status):
    assert "ep_events" in status
    ev = status["ep_events"]
    assert isinstance(ev, dict)


def test_status_has_body_state(status):
    assert "body_state" in status
    bs = status["body_state"]
    assert "size" in bs
    assert "shield" in bs


def test_causal_relations_serializable(status):
    for rel in status["causal_relations"]:
        assert "cause" in rel
        assert "effect" in rel
        assert "confidence" in rel
