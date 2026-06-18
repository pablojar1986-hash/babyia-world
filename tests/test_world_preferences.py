"""Tests de PreferenceTracker."""

from pathlib import Path

from brain.preferences import PreferenceTracker, RETURN_WEIGHT, RISK_WEIGHT


def make_tracker(tmp: Path | None = None) -> PreferenceTracker:
    return PreferenceTracker(prefs_file=tmp)


def test_initial_score_is_zero():
    pt = make_tracker()
    assert pt.get_score("food_world") == 0.0


def test_update_and_get_score():
    pt = make_tracker()
    pt.update("food_world", reward=5.0, risk_events=0, returned_home=True, steps=30)
    score = pt.get_score("food_world")
    assert score > 0.0


def test_preference_formula_components():
    pt = make_tracker()
    # 1 visita: reward=10, riesgo=0, retorno=True, pasos=20
    pt.update("food_world", reward=10.0, risk_events=0, returned_home=True, steps=20)
    score = pt.get_score("food_world")
    # Esperado: 10 + 1*RETURN_WEIGHT - 0*RISK_WEIGHT - 20*0.05
    expected = 10.0 + 1.0 * RETURN_WEIGHT - 0.0 * RISK_WEIGHT - 20 * 0.05
    assert abs(score - expected) < 0.01


def test_high_risk_lowers_score():
    pt = make_tracker()
    pt.update("danger", reward=5.0, risk_events=10, returned_home=True, steps=40)
    score = pt.get_score("danger")
    assert score < 5.0  # riesgo reduce la preferencia


def test_best_world_selection():
    pt = make_tracker()
    pt.update("food_world", reward=8.0, risk_events=0, returned_home=True, steps=20)
    pt.update("danger_world", reward=2.0, risk_events=5, returned_home=False, steps=50)
    best = pt.best_world()
    assert best == "food_world"


def test_to_dict_has_score():
    pt = make_tracker()
    pt.update("food_world", reward=5.0, risk_events=0, returned_home=True, steps=30)
    d = pt.to_dict()
    assert "food_world" in d
    assert "preference_score" in d["food_world"]
    assert "visits" in d["food_world"]


def test_save_and_reload(tmp_path):
    f = tmp_path / "prefs.json"
    pt = PreferenceTracker(prefs_file=f)
    pt.update("food_world", reward=5.0, risk_events=0, returned_home=True, steps=30)
    pt.save()
    assert f.exists()
    content = f.read_text()
    assert "food_world" in content
