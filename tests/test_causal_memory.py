"""Tests de brain/causal_memory.py."""

import pytest
from brain.causal_memory import CausalMemory, CausalRelation


@pytest.fixture
def tmp_cm(tmp_path):
    return CausalMemory(tmp_path / "causal.json")


def test_initial_empty(tmp_cm):
    assert len(tmp_cm.all_relations()) == 0


def test_observe_creates_relation(tmp_cm):
    tmp_cm.observe("powerup_fire", "fire_immunity", success=True, episode=1)
    assert tmp_cm.get_confidence("powerup_fire", "fire_immunity") == pytest.approx(1.0)


def test_confidence_with_mixed_evidence(tmp_cm):
    tmp_cm.observe("mud", "reduce_speed", success=True, episode=1)
    tmp_cm.observe("mud", "reduce_speed", success=True, episode=2)
    tmp_cm.observe("mud", "reduce_speed", success=False, episode=3)
    conf = tmp_cm.get_confidence("mud", "reduce_speed")
    assert conf == pytest.approx(2 / 3, abs=1e-3)


def test_get_confidence_unknown_returns_zero(tmp_cm):
    assert tmp_cm.get_confidence("unknown_cause", "unknown_effect") == 0.0


def test_best_effect_for_returns_highest_confidence(tmp_cm):
    tmp_cm.observe("fire_zone", "damage", success=True, episode=1)
    tmp_cm.observe("fire_zone", "damage", success=True, episode=2)
    tmp_cm.observe("fire_zone", "damage", success=True, episode=3)
    tmp_cm.observe("fire_zone", "slow", success=False, episode=1)
    tmp_cm.observe("fire_zone", "slow", success=False, episode=2)
    tmp_cm.observe("fire_zone", "slow", success=False, episode=3)
    best = tmp_cm.best_effect_for("fire_zone")
    assert best == "damage"


def test_count_learned_threshold(tmp_cm):
    for i in range(5):
        tmp_cm.observe("cause_a", "effect_a", success=True, episode=i)
    assert tmp_cm.count_learned(min_confidence=0.6) == 1


def test_count_learned_below_threshold(tmp_cm):
    tmp_cm.observe("c", "e", success=True, episode=1)
    tmp_cm.observe("c", "e", success=False, episode=2)
    assert tmp_cm.count_learned(min_confidence=0.9) == 0


def test_save_and_reload(tmp_path):
    path = tmp_path / "causal.json"
    cm1 = CausalMemory(path)
    cm1.observe("key", "opens_door", success=True, episode=5)
    cm1.save()

    cm2 = CausalMemory(path)
    assert cm2.get_confidence("key", "opens_door") == pytest.approx(1.0)


def test_reset_clears_all(tmp_cm):
    tmp_cm.observe("x", "y", success=True, episode=1)
    tmp_cm.reset()
    assert len(tmp_cm.all_relations()) == 0


def test_to_dict_structure(tmp_cm):
    tmp_cm.observe("a", "b", success=True, episode=1)
    d = tmp_cm.to_dict()
    assert "total_relations" in d
    assert "learned_confident" in d
    assert "relations" in d


def test_causal_relation_confidence_property():
    r = CausalRelation(cause="c", effect="e", successes=3, failures=1)
    assert r.confidence == pytest.approx(0.75)


def test_causal_relation_total_observations():
    r = CausalRelation(cause="c", effect="e", successes=2, failures=2)
    assert r.total_observations == 4
