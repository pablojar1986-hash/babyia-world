"""Tests de CausalMemory con eventos reales de powerup/hazard/puerta (0.4.2)."""

import pytest
from pathlib import Path
import tempfile
from brain.causal_memory import CausalMemory


def _mem():
    tmp = Path(tempfile.mktemp(suffix=".json"))
    return CausalMemory(tmp)


def test_observe_powerup_creates_relation():
    mem = _mem()
    mem.observe("growth_crystal", "increase_size", success=True, episode=1)
    rels = mem.all_relations()
    assert any(r.cause == "growth_crystal" for r in rels)


def test_observe_hazard_blocked():
    mem = _mem()
    mem.observe("fire_zone", "blocked_by_immunity", success=True, episode=1)
    mem.observe("fire_zone", "blocked_by_immunity", success=True, episode=2)
    rel = next(r for r in mem.all_relations() if r.cause == "fire_zone")
    assert rel.confidence > 0.5


def test_observe_hazard_unblocked():
    mem = _mem()
    mem.observe("spikes", "energy_damage", success=False, episode=1)
    rel = next(r for r in mem.all_relations() if r.cause == "spikes")
    assert rel.failures == 1
    assert rel.confidence == pytest.approx(0.0)


def test_observe_door_pass():
    mem = _mem()
    mem.observe("heavy_door", "passed", success=True, episode=1)
    mem.observe("heavy_door", "passed", success=True, episode=2)
    mem.observe("heavy_door", "passed", success=False, episode=3)
    rel = next(r for r in mem.all_relations() if r.cause == "heavy_door")
    assert rel.confidence == pytest.approx(2 / 3, abs=0.001)


def test_observe_small_door_fail():
    mem = _mem()
    mem.observe("small_door", "blocked_size_too_large", success=True, episode=5)
    rel = next(
        r
        for r in mem.all_relations()
        if r.cause == "small_door" and r.effect == "blocked_size_too_large"
    )
    assert rel.successes == 1


def test_count_learned_increases():
    mem = _mem()
    before = mem.count_learned()
    for i in range(5):
        mem.observe("energy_food", "energy_restore", success=True, episode=i)
    after = mem.count_learned()
    assert after >= before


def test_all_relations_returns_list():
    mem = _mem()
    assert isinstance(mem.all_relations(), list)


def test_to_dict_has_confidence():
    mem = _mem()
    mem.observe("shield_orb", "add_shield", success=True, episode=1)
    rels = mem.all_relations()
    d = rels[0].to_dict()
    assert "confidence" in d
    assert isinstance(d["confidence"], float)
