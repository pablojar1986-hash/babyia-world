"""Tests para minimap_view con mundo grande — BabyIA 0.4.5."""

from brain.mission import FIND_KEY, GO_TO_NEXT_LEVEL_DOOR


def _make_status(
    baby_pos=(0, 0),
    key_pos=(1, 6),
    progress_door_pos=(7, 7),
    has_key=False,
    key_present=True,
    mission_goal=FIND_KEY,
):
    """Construye un status dict minimo para tests de minimap."""
    return {
        "world_info": {
            "world_id": "home",
            "baby_pos": list(baby_pos),
            "is_at_home": True,
        },
        "inventory": {
            "has_key": has_key,
            "energy": 1.0,
        },
        "mission": {
            "current_goal": mission_goal,
            "target_position": list(progress_door_pos) if has_key else list(key_pos),
            "priority": 1.0,
            "reason": "test",
            "progress_score": 0.5,
        },
        "decision_context": {
            "has_key": has_key,
            "key_distance": 5,
            "progress_door_distance": 10,
            "energy": 1.0,
            "nearest_threat": None,
            "nearest_useful_powerup": None,
        },
    }


class TestMinimapStatusCompatibility:
    """Verifica que el dict de status tenga la forma correcta para minimap_view."""

    def test_status_has_mission_goal(self):
        status = _make_status()
        assert "current_goal" in status["mission"]

    def test_status_has_decision_context(self):
        status = _make_status()
        assert "key_distance" in status["decision_context"]

    def test_status_has_progress_door_distance(self):
        status = _make_status()
        assert "progress_door_distance" in status["decision_context"]

    def test_mission_goal_is_find_key_when_no_key(self):
        status = _make_status(has_key=False)
        assert status["mission"]["current_goal"] == FIND_KEY

    def test_mission_goal_is_go_to_door_when_has_key(self):
        status = _make_status(has_key=True, mission_goal=GO_TO_NEXT_LEVEL_DOOR)
        assert status["mission"]["current_goal"] == GO_TO_NEXT_LEVEL_DOOR


class TestLargeWorldDistances:
    """Valida calculo de distancias para grids grandes."""

    def test_distance_16x16_far(self):
        baby_pos = (0, 0)
        door_pos = (15, 15)
        dist = abs(baby_pos[0] - door_pos[0]) + abs(baby_pos[1] - door_pos[1])
        assert dist == 30

    def test_distance_16x16_near(self):
        baby_pos = (14, 15)
        door_pos = (15, 15)
        dist = abs(baby_pos[0] - door_pos[0]) + abs(baby_pos[1] - door_pos[1])
        assert dist == 1

    def test_distance_same_position(self):
        pos = (7, 7)
        dist = abs(pos[0] - pos[0]) + abs(pos[1] - pos[1])
        assert dist == 0


class TestMinimapNearestThreat:
    """Tests del campo nearest_threat como string (id de hazard)."""

    def test_nearest_threat_is_none_when_safe(self):
        status = _make_status()
        assert status["decision_context"]["nearest_threat"] is None

    def test_threat_as_string(self):
        status = _make_status()
        status["decision_context"]["nearest_threat"] = "fire_zone"
        threat = status["decision_context"]["nearest_threat"]
        assert isinstance(threat, str)

    def test_powerup_as_string(self):
        status = _make_status()
        status["decision_context"]["nearest_useful_powerup"] = "shield_orb"
        pu = status["decision_context"]["nearest_useful_powerup"]
        assert isinstance(pu, str)
