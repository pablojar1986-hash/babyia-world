"""Tests 0.4.4: MissionState dataclass y MissionTracker.compute()."""

from brain.mission import (
    MissionState,
    MissionTracker,
    FIND_KEY,
    GO_TO_NEXT_LEVEL_DOOR,
    AVOID_DANGER,
    LEVEL_COMPLETED,
    KEY_POS,
    PROGRESS_DOOR_POS,
    LOW_ENERGY_THRESHOLD,
)


def _tracker() -> MissionTracker:
    return MissionTracker()


class TestMissionState:
    def test_default_goal_is_find_key(self):
        ms = MissionState()
        assert ms.current_goal == FIND_KEY

    def test_to_dict_has_all_fields(self):
        ms = MissionState(
            current_goal=GO_TO_NEXT_LEVEL_DOOR,
            target_position=(7, 7),
            priority=1.0,
            reason="Test",
            progress_score=0.5,
        )
        d = ms.to_dict()
        assert "current_goal" in d
        assert "target_position" in d
        assert "priority" in d
        assert "reason" in d
        assert "progress_score" in d

    def test_target_position_serialized_as_list(self):
        ms = MissionState(target_position=(1, 6))
        d = ms.to_dict()
        assert d["target_position"] == [1, 6]

    def test_target_none_serialized_as_none(self):
        ms = MissionState(target_position=None)
        d = ms.to_dict()
        assert d["target_position"] is None


class TestMissionTrackerLevelCompleted:
    def test_level_completed_returns_level_completed_goal(self):
        t = _tracker()
        ms = t.compute(
            has_key=True,
            level_completed=True,
            energy=1.0,
            danger_nearby=False,
            has_shield=False,
            is_at_home=True,
            step_count=10,
            baby_pos=(7, 7),
            key_present=False,
        )
        assert ms.current_goal == LEVEL_COMPLETED

    def test_level_completed_priority_is_1(self):
        t = _tracker()
        ms = t.compute(
            has_key=True,
            level_completed=True,
            energy=0.1,
            danger_nearby=True,
            has_shield=False,
            is_at_home=False,
            step_count=100,
            baby_pos=(7, 7),
            key_present=False,
        )
        assert ms.priority == 1.0
        assert ms.progress_score == 1.0

    def test_level_completed_target_is_progress_door(self):
        t = _tracker()
        ms = t.compute(
            has_key=True,
            level_completed=True,
            energy=1.0,
            danger_nearby=False,
            has_shield=False,
            is_at_home=True,
            step_count=1,
            baby_pos=(0, 0),
            key_present=False,
        )
        assert ms.target_position == PROGRESS_DOOR_POS


class TestMissionTrackerAvoidDanger:
    def test_avoid_danger_when_no_shield_low_energy(self):
        t = _tracker()
        ms = t.compute(
            has_key=False,
            level_completed=False,
            energy=LOW_ENERGY_THRESHOLD - 0.01,
            danger_nearby=True,
            has_shield=False,
            is_at_home=False,
            step_count=5,
            baby_pos=(3, 3),
            key_present=True,
        )
        assert ms.current_goal == AVOID_DANGER

    def test_no_avoid_danger_when_has_shield(self):
        t = _tracker()
        ms = t.compute(
            has_key=False,
            level_completed=False,
            energy=0.1,
            danger_nearby=True,
            has_shield=True,
            is_at_home=False,
            step_count=5,
            baby_pos=(3, 3),
            key_present=True,
        )
        # Has shield — should not be AVOID_DANGER
        assert ms.current_goal != AVOID_DANGER

    def test_no_avoid_danger_when_energy_ok(self):
        t = _tracker()
        ms = t.compute(
            has_key=False,
            level_completed=False,
            energy=0.5,
            danger_nearby=True,
            has_shield=False,
            is_at_home=False,
            step_count=5,
            baby_pos=(3, 3),
            key_present=True,
        )
        assert ms.current_goal != AVOID_DANGER


class TestMissionTrackerFindKeyAndDoor:
    def test_has_key_gives_go_to_door(self):
        t = _tracker()
        ms = t.compute(
            has_key=True,
            level_completed=False,
            energy=1.0,
            danger_nearby=False,
            has_shield=False,
            is_at_home=True,
            step_count=5,
            baby_pos=(0, 0),
            key_present=False,
        )
        assert ms.current_goal == GO_TO_NEXT_LEVEL_DOOR
        assert ms.target_position == PROGRESS_DOOR_POS

    def test_no_key_gives_find_key(self):
        t = _tracker()
        ms = t.compute(
            has_key=False,
            level_completed=False,
            energy=1.0,
            danger_nearby=False,
            has_shield=False,
            is_at_home=True,
            step_count=5,
            baby_pos=(0, 0),
            key_present=True,
        )
        assert ms.current_goal == FIND_KEY
        assert ms.target_position == KEY_POS

    def test_progress_score_increases_closer_to_key(self):
        t = _tracker()
        far = t.compute(
            has_key=False,
            level_completed=False,
            energy=1.0,
            danger_nearby=False,
            has_shield=False,
            is_at_home=True,
            step_count=1,
            baby_pos=(7, 7),
            key_present=True,
        )
        near = t.compute(
            has_key=False,
            level_completed=False,
            energy=1.0,
            danger_nearby=False,
            has_shield=False,
            is_at_home=True,
            step_count=1,
            baby_pos=(1, 6),
            key_present=True,
        )
        assert near.progress_score > far.progress_score

    def test_progress_score_increases_closer_to_door(self):
        t = _tracker()
        far = t.compute(
            has_key=True,
            level_completed=False,
            energy=1.0,
            danger_nearby=False,
            has_shield=False,
            is_at_home=True,
            step_count=1,
            baby_pos=(0, 0),
            key_present=False,
        )
        near = t.compute(
            has_key=True,
            level_completed=False,
            energy=1.0,
            danger_nearby=False,
            has_shield=False,
            is_at_home=True,
            step_count=1,
            baby_pos=(7, 7),
            key_present=False,
        )
        assert near.progress_score > far.progress_score
