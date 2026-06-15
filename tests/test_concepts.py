"""Tests de ConceptMemory (brain/concepts.py)."""
import json
import pytest
from pathlib import Path
from brain.concepts import ConceptMemory, CONFIDENCE_THRESHOLD, CONFIDENCE_GAIN_OK, CONFIDENCE_LOSS


def make_cm(tmp_path) -> ConceptMemory:
    return ConceptMemory(concepts_file=tmp_path / "test_concepts.json")


def test_starts_empty(tmp_path):
    cm = make_cm(tmp_path)
    assert cm.total() == 0


def test_observe_creates_concept(tmp_path):
    cm = make_cm(tmp_path)
    cm.observe({"key_opens": "door"}, success=True, episode=1)
    assert cm.total() == 1


def test_success_increases_confidence(tmp_path):
    cm = make_cm(tmp_path)
    cm.observe({"key_opens": "door"}, success=True, episode=1)
    c0 = cm.top_concepts()[0]["confidence"]
    cm.observe({"key_opens": "door"}, success=True, episode=2)
    c1 = cm.top_concepts()[0]["confidence"]
    assert c1 > c0


def test_failure_decreases_confidence(tmp_path):
    cm = make_cm(tmp_path)
    cm.observe({"key_opens": "door"}, success=True, episode=1)
    cm.observe({"key_opens": "door"}, success=True, episode=2)
    c0 = cm.top_concepts()[0]["confidence"]
    cm.observe({"key_opens": "door"}, success=False, episode=3)
    c1 = cm.top_concepts()[0]["confidence"]
    assert c1 < c0


def test_is_learned_below_threshold(tmp_path):
    cm = make_cm(tmp_path)
    cm.observe({"key_opens": "door"}, success=True, episode=1)
    assert cm.is_learned("key_opens:door") is False  # solo 1 observacion


def test_is_learned_above_threshold(tmp_path):
    cm = make_cm(tmp_path)
    key = "key_opens:door"
    for ep in range(10):
        cm.observe({"key_opens": "door"}, success=True, episode=ep)
    assert cm.is_learned(key) is True


def test_confidence_clamped_to_1(tmp_path):
    cm = make_cm(tmp_path)
    for ep in range(20):
        cm.observe({"key_opens": "door"}, success=True, episode=ep)
    assert cm.top_concepts()[0]["confidence"] <= 1.0


def test_save_and_reload(tmp_path):
    cm = make_cm(tmp_path)
    cm.observe({"key_opens": "door"}, success=True, episode=1)
    cm.save()
    cm2 = make_cm(tmp_path)
    assert cm2.total() == 1


def test_json_format(tmp_path):
    path = tmp_path / "test_concepts.json"
    cm = ConceptMemory(concepts_file=path)
    cm.observe({"food_restores": "energy"}, success=True, episode=5)
    cm.save()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "concepts" in data
    assert len(data["concepts"]) == 1
    c = data["concepts"][0]
    assert "confidence" in c
    assert "evidence_count" in c
    assert "first_discovered_episode" in c


def test_reset_clears_file(tmp_path):
    path = tmp_path / "test_concepts.json"
    cm = ConceptMemory(concepts_file=path)
    cm.observe({"x": "y"}, success=True, episode=1)
    cm.save()
    cm.reset()
    assert cm.total() == 0
    assert not path.exists()


def test_top_concepts_returns_n(tmp_path):
    cm = make_cm(tmp_path)
    for key in ["a:1", "b:1", "c:1", "d:1"]:
        rel, val = key.split(":")
        cm.observe({rel: val}, success=True, episode=1)
    assert len(cm.top_concepts(3)) == 3
