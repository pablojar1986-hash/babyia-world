import numpy as np
import pytest
from brain.memory import Memory


@pytest.fixture
def mem():
    m = Memory()
    m.episodes = []
    m.autobiography = []
    return m


def test_record_step_stores_entry(mem):
    state = np.zeros(10, dtype=np.float32)
    mem.record_step(1, 1, state, 2, -0.05, {"hit_wall": False, "reached_goal": False})
    assert len(mem.episodes) == 1
    assert mem.episodes[0]["episode"] == 1
    assert mem.episodes[0]["action"] == 2


def test_record_autobiography(mem):
    mem.record_autobiography("Hoy aprendí algo nuevo.")
    assert len(mem.autobiography) == 1
    assert mem.autobiography[0]["text"] == "Hoy aprendí algo nuevo."


def test_last_log_entries(mem):
    for i in range(10):
        mem.record_autobiography(f"Entrada {i}")
    entries = mem.last_log_entries(3)
    assert len(entries) == 3
    assert entries[-1] == "Entrada 9"


def test_generate_phrase_goal(mem):
    phrase = mem.generate_phrase(10, 9.0, 0, True, 0.3)
    assert "meta" in phrase.lower() or "alcancé" in phrase.lower()


def test_generate_phrase_wall(mem):
    phrase = mem.generate_phrase(5, -3.0, 12, False, 0.8)
    assert (
        "pared" in phrase.lower()
        or "choqué" in phrase.lower()
        or "estrategia" in phrase.lower()
    )


def test_ram_limit(mem):
    state = np.zeros(10, dtype=np.float32)
    for i in range(1100):
        mem.record_step(i, 1, state, 0, 0.0, {"hit_wall": False, "reached_goal": False})
    assert len(mem.episodes) <= 1000
