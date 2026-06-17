"""Tests 0.4.4: MissionReward.compute() y reset_episode()."""

from brain.mission_reward import (
    MissionReward,
    APPROACH_KEY_BONUS,
    APPROACH_DOOR_BONUS,
    MISSION_SWITCH_BONUS,
    MOVE_AWAY_PENALTY,
    OPTIONAL_DISTRACTION_PENALTY,
)
from brain.mission import FIND_KEY, GO_TO_NEXT_LEVEL_DOOR


def _ctx(goal=FIND_KEY, key_dist=0.5, prog_dist=0.8, has_key=False) -> dict:
    return {
        "current_goal": goal,
        "key_distance": key_dist,
        "progress_door_distance": prog_dist,
        "has_key": has_key,
    }


class TestMissionRewardReset:
    def test_initial_state_zero(self):
        mr = MissionReward()
        assert mr.total_mission_reward == 0.0
        assert mr.progress_steps == 0
        assert mr.regression_steps == 0
        assert mr.mission_switches == 0

    def test_reset_clears_accumulated(self):
        mr = MissionReward()
        prev = _ctx(FIND_KEY, key_dist=0.5)
        curr = _ctx(FIND_KEY, key_dist=0.3)
        mr.compute(prev, curr, {})
        mr.reset_episode()
        assert mr.total_mission_reward == 0.0
        assert mr.progress_steps == 0

    def test_to_dict_has_all_fields(self):
        mr = MissionReward()
        d = mr.to_dict()
        assert "total_mission_reward" in d
        assert "progress_steps" in d
        assert "regression_steps" in d
        assert "mission_switches" in d


class TestApproachKeyBonus:
    def test_approach_key_gives_bonus(self):
        mr = MissionReward()
        prev = _ctx(FIND_KEY, key_dist=0.5)
        curr = _ctx(FIND_KEY, key_dist=0.3)
        delta = mr.compute(prev, curr, {})
        assert delta == APPROACH_KEY_BONUS
        assert mr.progress_steps == 1

    def test_move_away_key_gives_penalty(self):
        mr = MissionReward()
        prev = _ctx(FIND_KEY, key_dist=0.3)
        curr = _ctx(FIND_KEY, key_dist=0.5)
        delta = mr.compute(prev, curr, {})
        assert delta == MOVE_AWAY_PENALTY
        assert mr.regression_steps == 1

    def test_no_reward_for_stationary_key_distance(self):
        mr = MissionReward()
        prev = _ctx(FIND_KEY, key_dist=0.5)
        curr = _ctx(FIND_KEY, key_dist=0.5)
        delta = mr.compute(prev, curr, {})
        assert delta == 0.0


class TestApproachDoorBonus:
    def test_approach_door_gives_bonus(self):
        mr = MissionReward()
        prev = _ctx(GO_TO_NEXT_LEVEL_DOOR, prog_dist=0.8)
        curr = _ctx(GO_TO_NEXT_LEVEL_DOOR, prog_dist=0.5)
        delta = mr.compute(prev, curr, {})
        assert delta == APPROACH_DOOR_BONUS
        assert mr.progress_steps == 1

    def test_move_away_door_gives_penalty(self):
        mr = MissionReward()
        prev = _ctx(GO_TO_NEXT_LEVEL_DOOR, prog_dist=0.4)
        curr = _ctx(GO_TO_NEXT_LEVEL_DOOR, prog_dist=0.7)
        delta = mr.compute(prev, curr, {})
        assert delta == MOVE_AWAY_PENALTY
        assert mr.regression_steps == 1


class TestMissionSwitchBonus:
    def test_switch_find_key_to_door_gives_bonus(self):
        mr = MissionReward()
        prev = _ctx(FIND_KEY)
        curr = _ctx(GO_TO_NEXT_LEVEL_DOOR, prog_dist=0.5)
        delta = mr.compute(prev, curr, {})
        # Also has approach door bonus
        assert MISSION_SWITCH_BONUS in [delta, delta - APPROACH_DOOR_BONUS]
        assert mr.mission_switches == 1

    def test_no_switch_bonus_for_same_goal(self):
        mr = MissionReward()
        prev = _ctx(FIND_KEY, key_dist=0.5)
        curr = _ctx(FIND_KEY, key_dist=0.5)
        mr.compute(prev, curr, {})
        assert mr.mission_switches == 0


class TestOptionalRoomPenalty:
    def test_treasure_room_without_key_penalized(self):
        mr = MissionReward()
        prev = _ctx(FIND_KEY, key_dist=0.5)
        curr = _ctx(FIND_KEY, key_dist=0.5, has_key=False)
        delta = mr.compute(prev, curr, {"entered_treasure_room": True})
        assert delta == OPTIONAL_DISTRACTION_PENALTY

    def test_treasure_room_with_key_not_penalized(self):
        mr = MissionReward()
        prev = _ctx(GO_TO_NEXT_LEVEL_DOOR, has_key=True)
        curr = _ctx(GO_TO_NEXT_LEVEL_DOOR, has_key=True)
        delta = mr.compute(prev, curr, {"entered_treasure_room": True})
        assert delta == 0.0

    def test_total_mission_reward_accumulates(self):
        mr = MissionReward()
        prev1 = _ctx(FIND_KEY, key_dist=0.5)
        curr1 = _ctx(FIND_KEY, key_dist=0.3)
        mr.compute(prev1, curr1, {})
        prev2 = _ctx(FIND_KEY, key_dist=0.3)
        curr2 = _ctx(FIND_KEY, key_dist=0.1)
        mr.compute(prev2, curr2, {})
        assert mr.total_mission_reward == round(APPROACH_KEY_BONUS * 2, 5)
        assert mr.progress_steps == 2


class TestMissionRewardMagnitudes:
    def test_all_shaping_below_level_completion(self):
        """Reward shaping no debe superar REWARD_LEVEL_COMPLETED."""
        from world.rewards import REWARD_LEVEL_COMPLETED

        assert APPROACH_KEY_BONUS < REWARD_LEVEL_COMPLETED
        assert APPROACH_DOOR_BONUS < REWARD_LEVEL_COMPLETED
        assert MISSION_SWITCH_BONUS < REWARD_LEVEL_COMPLETED
        assert abs(MOVE_AWAY_PENALTY) < REWARD_LEVEL_COMPLETED
        assert abs(OPTIONAL_DISTRACTION_PENALTY) < REWARD_LEVEL_COMPLETED
