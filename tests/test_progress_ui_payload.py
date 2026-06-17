"""Tests 0.4.3: payload de get_status() incluye campos de progresion."""

from brain.trainer import Trainer


def _make_trainer() -> Trainer:
    t = Trainer(training=False)
    t.start_episode()
    return t


class TestProgressUIPayload:
    def test_status_has_current_objective(self):
        t = _make_trainer()
        s = t.get_status()
        assert "current_objective" in s
        assert isinstance(s["current_objective"], str)
        assert len(s["current_objective"]) > 0

    def test_status_has_episodes_without_progress(self):
        t = _make_trainer()
        s = t.get_status()
        assert "episodes_without_progress" in s
        assert isinstance(s["episodes_without_progress"], int)

    def test_status_has_stagnation_active(self):
        t = _make_trainer()
        s = t.get_status()
        assert "stagnation_active" in s
        assert isinstance(s["stagnation_active"], bool)

    def test_status_has_level_completions(self):
        t = _make_trainer()
        s = t.get_status()
        assert "level_completions" in s
        assert isinstance(s["level_completions"], int)

    def test_status_has_curriculum_dict(self):
        t = _make_trainer()
        s = t.get_status()
        assert "curriculum" in s
        c = s["curriculum"]
        assert "current_level" in c
        assert "required" in c
        assert "completed_so_far" in c

    def test_status_has_ep_level_completed(self):
        t = _make_trainer()
        s = t.get_status()
        assert "ep_level_completed" in s
        assert s["ep_level_completed"] is False

    def test_status_has_ep_optional_rooms(self):
        t = _make_trainer()
        s = t.get_status()
        assert "ep_optional_rooms" in s
        assert isinstance(s["ep_optional_rooms"], int)

    def test_status_has_ep_treasure_rooms(self):
        t = _make_trainer()
        s = t.get_status()
        assert "ep_treasure_rooms" in s

    def test_status_has_ep_training_rooms(self):
        t = _make_trainer()
        s = t.get_status()
        assert "ep_training_rooms" in s

    def test_status_has_ep_next_door_blocked(self):
        t = _make_trainer()
        s = t.get_status()
        assert "ep_next_door_blocked" in s

    def test_current_objective_changes_with_key(self):
        t = _make_trainer()
        t.inventory.pick_key()
        s = t.get_status()
        obj = s["current_objective"]
        assert (
            "llave" not in obj.lower()
            or "dorada" in obj.lower()
            or "puerta" in obj.lower()
        )

    def test_episodes_without_progress_starts_at_zero(self):
        t = _make_trainer()
        s = t.get_status()
        assert s["episodes_without_progress"] == 0

    def test_status_has_has_key(self):
        t = _make_trainer()
        s = t.get_status()
        assert "has_key" in s
        assert s["has_key"] is False

    def test_has_key_true_after_pick_key(self):
        t = _make_trainer()
        t.inventory.pick_key()
        s = t.get_status()
        assert s["has_key"] is True
