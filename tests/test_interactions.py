"""Tests de logica de interaccion (world/interactions.py)."""
from world.interactions import (
    interact_danger,
    interact_door_closed,
    interact_food,
    interact_key,
    interact_unknown,
)


def _assert_structure(result):
    assert "success" in result
    assert "message" in result
    assert "reward_delta" in result
    assert "concept_signal" in result


# ── interact_key ──────────────────────────────────────────────────────────────

def test_pick_key_first_time():
    r = interact_key(has_key=False, first_time=True)
    assert r["success"] is True
    assert r["reward_delta"] == 3.0
    assert "key_found" in r["concept_signal"]
    _assert_structure(r)


def test_pick_key_extra():
    r = interact_key(has_key=False, first_time=False)
    assert r["success"] is True
    assert r["reward_delta"] == 0.5


def test_pick_key_already_has_key():
    r = interact_key(has_key=True, first_time=False)
    assert r["success"] is False
    assert r["reward_delta"] == 0.0


# ── interact_door_closed ──────────────────────────────────────────────────────

def test_door_without_key():
    r = interact_door_closed(has_key=False)
    assert r["success"] is False
    assert r["reward_delta"] == -0.5
    assert "door_requires" in r["concept_signal"]
    _assert_structure(r)


def test_door_with_key():
    r = interact_door_closed(has_key=True)
    assert r["success"] is True
    assert r["reward_delta"] == 5.0
    assert r["concept_signal"].get("key_opens") == "door"


# ── interact_food ─────────────────────────────────────────────────────────────

def test_food_when_low_energy():
    r = interact_food(energy=0.3)
    assert r["success"] is True
    assert r["reward_delta"] == 2.0
    _assert_structure(r)


def test_food_when_ok_energy():
    r = interact_food(energy=0.8)
    assert r["success"] is True
    assert r["reward_delta"] == 0.5


# ── interact_danger ───────────────────────────────────────────────────────────

def test_danger_always_fails():
    r = interact_danger()
    assert r["success"] is False
    assert r["reward_delta"] == -2.0
    assert "danger_reduces" in r["concept_signal"]
    _assert_structure(r)


# ── interact_unknown ──────────────────────────────────────────────────────────

def test_unknown_first_time():
    r = interact_unknown(first_time=True)
    assert r["success"] is True
    assert r["reward_delta"] == 1.0
    _assert_structure(r)


def test_unknown_repeat():
    r = interact_unknown(first_time=False)
    assert r["reward_delta"] == 0.0


def test_all_return_correct_structure():
    for fn in [
        lambda: interact_key(False, True),
        lambda: interact_door_closed(False),
        lambda: interact_food(0.5),
        lambda: interact_danger(),
        lambda: interact_unknown(True),
    ]:
        _assert_structure(fn())
