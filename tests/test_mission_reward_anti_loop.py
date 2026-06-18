"""Tests para MissionReward — penalizaciones anti-estancamiento (0.4.6b)."""

import pytest
from brain.mission_reward import (
    MissionReward,
    MAX_MISSION_REWARD_PER_EPISODE,
    WALL_REPEAT_PENALTY,
    HAZARD_REPEAT_PENALTY,
    _OSCILLATION_THRESHOLD,
    _RECENT_POS_WINDOW,
)
from brain.mission import FIND_KEY


def _ctx(goal=FIND_KEY, key_dist=0.5, door_dist=0.5, has_key=False):
    return {
        "current_goal": goal,
        "key_distance": key_dist,
        "progress_door_distance": door_dist,
        "has_key": has_key,
    }


@pytest.fixture
def mr():
    m = MissionReward()
    m.reset_episode()
    return m


class TestWallRepeatPenalty:
    def test_no_penalty_without_repeated_wall(self, mr):
        delta = mr.compute(_ctx(), _ctx(), {"repeated_wall": False})
        assert delta == pytest.approx(0.0, abs=0.5)

    def test_penalty_applied_on_repeated_wall(self, mr):
        delta = mr.compute(_ctx(), _ctx(), {"repeated_wall": True})
        assert delta <= WALL_REPEAT_PENALTY + 0.01


class TestHazardRepeatPenalty:
    def test_no_penalty_without_repeated_hazard(self, mr):
        delta = mr.compute(_ctx(), _ctx(), {"repeated_hazard": False})
        assert delta == pytest.approx(0.0, abs=0.5)

    def test_penalty_applied_on_repeated_hazard(self, mr):
        delta = mr.compute(_ctx(), _ctx(), {"repeated_hazard": True})
        assert delta <= HAZARD_REPEAT_PENALTY + 0.01


class TestOscillationPenalty:
    def test_no_penalty_below_threshold(self, mr):
        pos = (2, 2)
        for _ in range(_OSCILLATION_THRESHOLD - 1):
            mr.compute(_ctx(), _ctx(), {}, baby_pos=pos)
        # Sin alcanzar el umbral, no debe haber penalizacion de oscilacion
        assert mr.oscillation_steps == 0

    def test_penalty_at_threshold(self, mr):
        pos = (3, 3)
        for _ in range(_OSCILLATION_THRESHOLD):
            mr.compute(_ctx(), _ctx(), {}, baby_pos=pos)
        assert mr.oscillation_steps >= 1

    def test_window_limits_history(self, mr):
        # Llenar la ventana con posiciones diferentes, luego repetir una
        for i in range(_RECENT_POS_WINDOW):
            mr.compute(_ctx(), _ctx(), {}, baby_pos=(i, 0))
        # La posicion (0,0) ya no deberia estar en la ventana
        assert len(mr._recent_positions) <= _RECENT_POS_WINDOW


class TestEpisodeCap:
    def test_positive_reward_capped_at_max(self, mr):
        # Forzar total_mission_reward al limite
        mr.total_mission_reward = MAX_MISSION_REWARD_PER_EPISODE

        # Intento de acercarse a llave (deberia dar delta > 0, pero es capado)
        prev = _ctx(key_dist=0.8)
        curr = _ctx(key_dist=0.3)
        delta = mr.compute(prev, curr, {})
        assert delta == pytest.approx(0.0, abs=1e-6)

    def test_negative_reward_not_capped(self, mr):
        mr.total_mission_reward = MAX_MISSION_REWARD_PER_EPISODE
        delta = mr.compute(_ctx(), _ctx(), {"repeated_wall": True})
        # Las penalizaciones siguen aplicandose aunque se haya alcanzado el cap
        assert delta <= 0.0

    def test_cap_not_triggered_below_limit(self, mr):
        mr.total_mission_reward = MAX_MISSION_REWARD_PER_EPISODE - 1.0
        prev = _ctx(key_dist=0.8)
        curr = _ctx(key_dist=0.3)
        delta = mr.compute(prev, curr, {})
        assert delta > 0.0


class TestResetEpisode:
    def test_reset_clears_oscillation_steps(self, mr):
        for _ in range(5):
            mr.compute(_ctx(), _ctx(), {}, baby_pos=(1, 1))
        mr.reset_episode()
        assert mr.oscillation_steps == 0
        assert mr._recent_positions == []

    def test_reset_clears_total_reward(self, mr):
        mr.total_mission_reward = 5.0
        mr.reset_episode()
        assert mr.total_mission_reward == 0.0


class TestToDict:
    def test_oscillation_steps_in_dict(self, mr):
        d = mr.to_dict()
        assert "oscillation_steps" in d

    def test_oscillation_steps_counted(self, mr):
        pos = (4, 4)
        for _ in range(_OSCILLATION_THRESHOLD + 1):
            mr.compute(_ctx(), _ctx(), {}, baby_pos=pos)
        d = mr.to_dict()
        assert d["oscillation_steps"] >= 1
