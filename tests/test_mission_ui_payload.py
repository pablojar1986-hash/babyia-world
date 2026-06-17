"""Tests 0.4.4: get_status() incluye mission, decision_context y mission_reward."""

from brain.trainer import Trainer


def _make_trainer() -> Trainer:
    t = Trainer(training=False)
    t.start_episode()
    return t


class TestMissionUIPayload:
    def test_status_has_mission_key(self):
        t = _make_trainer()
        s = t.get_status()
        assert "mission" in s

    def test_mission_has_current_goal(self):
        t = _make_trainer()
        s = t.get_status()
        m = s["mission"]
        assert "current_goal" in m
        assert isinstance(m["current_goal"], str)
        assert len(m["current_goal"]) > 0

    def test_mission_has_progress_score(self):
        t = _make_trainer()
        s = t.get_status()
        m = s["mission"]
        assert "progress_score" in m
        assert isinstance(m["progress_score"], float)

    def test_mission_has_reason(self):
        t = _make_trainer()
        s = t.get_status()
        m = s["mission"]
        assert "reason" in m
        assert isinstance(m["reason"], str)

    def test_status_has_decision_context_key(self):
        t = _make_trainer()
        s = t.get_status()
        assert "decision_context" in s

    def test_decision_context_has_has_key(self):
        t = _make_trainer()
        s = t.get_status()
        ctx = s["decision_context"]
        assert "has_key" in ctx

    def test_decision_context_has_key_distance(self):
        t = _make_trainer()
        s = t.get_status()
        ctx = s["decision_context"]
        assert "key_distance" in ctx
        assert isinstance(ctx["key_distance"], float)

    def test_decision_context_has_progress_door_distance(self):
        t = _make_trainer()
        s = t.get_status()
        ctx = s["decision_context"]
        assert "progress_door_distance" in ctx

    def test_decision_context_has_energy(self):
        t = _make_trainer()
        s = t.get_status()
        ctx = s["decision_context"]
        assert "energy" in ctx

    def test_status_has_mission_reward_key(self):
        t = _make_trainer()
        s = t.get_status()
        assert "mission_reward" in s

    def test_mission_reward_has_total(self):
        t = _make_trainer()
        s = t.get_status()
        mr = s["mission_reward"]
        assert "total_mission_reward" in mr
        assert isinstance(mr["total_mission_reward"], float)

    def test_mission_reward_has_progress_steps(self):
        t = _make_trainer()
        s = t.get_status()
        mr = s["mission_reward"]
        assert "progress_steps" in mr
        assert isinstance(mr["progress_steps"], int)

    def test_mission_reward_has_regression_steps(self):
        t = _make_trainer()
        s = t.get_status()
        mr = s["mission_reward"]
        assert "regression_steps" in mr

    def test_mission_reward_has_mission_switches(self):
        t = _make_trainer()
        s = t.get_status()
        mr = s["mission_reward"]
        assert "mission_switches" in mr

    def test_initial_goal_is_find_key_without_key(self):
        t = _make_trainer()
        s = t.get_status()
        goal = s["mission"]["current_goal"]
        assert goal == "FIND_KEY"

    def test_mission_goal_is_string(self):
        # La mision se actualiza en cada step(); el test verifica el tipo del campo.
        t = _make_trainer()
        s = t.get_status()
        assert isinstance(s["mission"]["current_goal"], str)
