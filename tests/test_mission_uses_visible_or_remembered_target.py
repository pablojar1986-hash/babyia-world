"""Tests que MissionTracker usa percepcion y memoria visual — BabyIA 0.4.5b."""

from brain.mission import (
    MissionTracker,
    FIND_KEY,
    GO_TO_NEXT_LEVEL_DOOR,
    COLLECT_USEFUL_POWERUP,
)
from brain.visual_memory import VisualMemory


def _compute(
    has_key=False,
    level_completed=False,
    energy=1.0,
    danger_nearby=False,
    has_shield=False,
    baby_pos=(4, 4),
    key_present=True,
    key_pos=(1, 6),
    progress_door_pos=(7, 7),
    perception_result=None,
    visual_memory=None,
):
    tracker = MissionTracker()
    return tracker.compute(
        has_key=has_key,
        level_completed=level_completed,
        energy=energy,
        danger_nearby=danger_nearby,
        has_shield=has_shield,
        is_at_home=True,
        step_count=10,
        baby_pos=baby_pos,
        key_present=key_present,
        key_pos=key_pos,
        progress_door_pos=progress_door_pos,
        perception_result=perception_result,
        visual_memory=visual_memory,
    )


class TestMissionUsesVisibleTarget:
    def test_default_find_key(self):
        ms = _compute()
        assert ms.current_goal == FIND_KEY

    def test_uses_visible_key_position(self):
        perc = {
            "nearest_key": {"position": [3, 3], "distance": 2},
            "nearest_progress_door": None,
            "nearest_powerup": None,
        }
        ms = _compute(perception_result=perc)
        assert ms.current_goal == FIND_KEY
        assert ms.target_position == (3, 3)

    def test_uses_static_key_when_not_visible(self):
        ms = _compute()
        assert ms.target_position == (1, 6)

    def test_uses_remembered_key_from_visual_memory(self):
        vm = VisualMemory()
        vm.last_seen_key = [2, 5]
        ms = _compute(visual_memory=vm)
        assert ms.current_goal == FIND_KEY
        assert ms.target_position == (2, 5)

    def test_visible_overrides_memory(self):
        vm = VisualMemory()
        vm.last_seen_key = [2, 5]
        perc = {
            "nearest_key": {"position": [3, 3], "distance": 2},
            "nearest_progress_door": None,
            "nearest_powerup": None,
        }
        ms = _compute(perception_result=perc, visual_memory=vm)
        assert ms.target_position == (3, 3)

    def test_go_to_door_with_key(self):
        ms = _compute(has_key=True)
        assert ms.current_goal == GO_TO_NEXT_LEVEL_DOOR
        assert ms.target_position == (7, 7)

    def test_go_to_visible_door_position(self):
        perc = {
            "nearest_key": None,
            "nearest_progress_door": {"position": [7, 7], "distance": 4},
            "nearest_powerup": None,
        }
        ms = _compute(has_key=True, perception_result=perc)
        assert ms.current_goal == GO_TO_NEXT_LEVEL_DOOR
        assert ms.target_position == (7, 7)

    def test_uses_remembered_door_from_visual_memory(self):
        vm = VisualMemory()
        vm.last_seen_progress_door = [6, 6]
        ms = _compute(has_key=True, visual_memory=vm)
        assert ms.current_goal == GO_TO_NEXT_LEVEL_DOOR
        assert ms.target_position == (6, 6)


class TestMissionCollectUsefulPowerup:
    def test_collect_powerup_when_energy_low_and_visible(self):
        perc = {
            "nearest_key": None,
            "nearest_progress_door": None,
            "nearest_powerup": {"position": [3, 4], "distance": 2},
        }
        ms = _compute(energy=0.3, perception_result=perc)
        assert ms.current_goal == COLLECT_USEFUL_POWERUP
        assert ms.target_position == (3, 4)

    def test_no_powerup_mission_when_energy_high(self):
        perc = {
            "nearest_key": None,
            "nearest_progress_door": None,
            "nearest_powerup": {"position": [3, 4], "distance": 2},
        }
        ms = _compute(energy=0.8, perception_result=perc)
        assert ms.current_goal != COLLECT_USEFUL_POWERUP

    def test_no_powerup_mission_when_far(self):
        perc = {
            "nearest_key": None,
            "nearest_progress_door": None,
            "nearest_powerup": {"position": [3, 4], "distance": 4},
        }
        ms = _compute(energy=0.3, perception_result=perc)
        assert ms.current_goal != COLLECT_USEFUL_POWERUP

    def test_no_powerup_mission_when_has_key(self):
        perc = {
            "nearest_key": None,
            "nearest_progress_door": None,
            "nearest_powerup": {"position": [3, 4], "distance": 1},
        }
        ms = _compute(has_key=True, energy=0.2, perception_result=perc)
        assert ms.current_goal != COLLECT_USEFUL_POWERUP

    def test_no_powerup_mission_when_danger_nearby(self):
        perc = {
            "nearest_key": None,
            "nearest_progress_door": None,
            "nearest_powerup": {"position": [3, 4], "distance": 1},
        }
        ms = _compute(danger_nearby=True, energy=0.2, perception_result=perc)
        assert ms.current_goal != COLLECT_USEFUL_POWERUP
