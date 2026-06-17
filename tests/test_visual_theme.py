"""Tests 0.4.4: funciones de interface/visual_theme.py."""

from interface.visual_theme import (
    mission_color,
    distance_color,
    energy_color,
    blend_color,
    NEAR_COLOR,
    MID_COLOR,
    FAR_COLOR,
)


class TestMissionColor:
    def test_known_goals_return_tuple(self):
        for goal in [
            "FIND_KEY",
            "GO_TO_NEXT_LEVEL_DOOR",
            "AVOID_DANGER",
            "COLLECT_USEFUL_POWERUP",
            "RETURN_HOME",
            "LEVEL_COMPLETED",
            "EXPLORE_OPTIONAL_ROOM",
        ]:
            c = mission_color(goal)
            assert isinstance(c, tuple)
            assert len(c) == 3
            assert all(0 <= v <= 255 for v in c)

    def test_unknown_goal_returns_fallback(self):
        c = mission_color("UNKNOWN_GOAL")
        assert isinstance(c, tuple)
        assert len(c) == 3

    def test_find_key_is_yellow_ish(self):
        c = mission_color("FIND_KEY")
        r, g, b = c
        assert r > g  # red > green for yellow
        assert r > b

    def test_avoid_danger_is_red_ish(self):
        c = mission_color("AVOID_DANGER")
        r, g, b = c
        assert r > g
        assert r > b


class TestDistanceColor:
    def test_near_dist_returns_near_color(self):
        assert distance_color(0.1) == NEAR_COLOR

    def test_mid_dist_returns_mid_color(self):
        assert distance_color(0.5) == MID_COLOR

    def test_far_dist_returns_far_color(self):
        assert distance_color(0.9) == FAR_COLOR

    def test_exactly_at_boundary_near(self):
        # 0.3 is the boundary — should be MID (not near)
        assert distance_color(0.3) == MID_COLOR

    def test_exactly_at_boundary_far(self):
        assert distance_color(0.6) == FAR_COLOR


class TestEnergyColor:
    def test_high_energy_returns_green(self):
        c = energy_color(0.8)
        r, g, b = c
        assert g > r
        assert g > b

    def test_low_energy_returns_red(self):
        c = energy_color(0.1)
        r, g, b = c
        assert r > g
        assert r > b

    def test_boundary_at_04(self):
        # energy_color uses >= 0.4 for high
        high = energy_color(0.4)
        low = energy_color(0.39)
        assert high != low


class TestBlendColor:
    def test_t_zero_gives_c1(self):
        c1, c2 = (255, 0, 0), (0, 255, 0)
        assert blend_color(c1, c2, 0.0) == c1

    def test_t_one_gives_c2(self):
        c1, c2 = (255, 0, 0), (0, 255, 0)
        assert blend_color(c1, c2, 1.0) == c2

    def test_t_half_gives_midpoint(self):
        c1, c2 = (0, 0, 0), (100, 100, 100)
        result = blend_color(c1, c2, 0.5)
        assert result == (50, 50, 50)

    def test_clamp_t_below_zero(self):
        c1, c2 = (255, 0, 0), (0, 255, 0)
        assert blend_color(c1, c2, -1.0) == c1

    def test_clamp_t_above_one(self):
        c1, c2 = (255, 0, 0), (0, 255, 0)
        assert blend_color(c1, c2, 5.0) == c2

    def test_all_values_in_valid_range(self):
        c1, c2 = (10, 200, 50), (240, 30, 180)
        for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
            r = blend_color(c1, c2, t)
            assert all(0 <= v <= 255 for v in r)
