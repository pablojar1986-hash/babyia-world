"""Tests que PerceptionSystem respeta body_state.vision_range — BabyIA 0.4.5b."""

import types
import pytest
from world.grid_world import GridWorld
from world.world_config import DEFAULT_VISION_RANGE
from brain.perception import PerceptionSystem


def _empty_world(gs: int = 8) -> GridWorld:
    w = GridWorld(grid_size=gs)
    w.reset()
    return w


def _body(vision_range: int):
    return types.SimpleNamespace(vision_range=vision_range)


class TestPerceptionUsesBodyVisionRange:
    def test_default_range_when_no_body(self):
        sys = PerceptionSystem()
        w = _empty_world()
        result = sys.observe(w, (0, 0))
        assert result["vision_range"] == DEFAULT_VISION_RANGE

    def test_body_overrides_default(self):
        sys = PerceptionSystem()
        w = _empty_world()
        result = sys.observe(w, (4, 4), body_state=_body(5))
        assert result["vision_range"] == 5

    def test_reduced_vision_range_less_cells(self):
        sys = PerceptionSystem()
        w = _empty_world()
        r_small = sys.observe(w, (4, 4), body_state=_body(1))
        r_large = sys.observe(w, (4, 4), body_state=_body(4))
        assert len(r_small["visible_cells"]) < len(r_large["visible_cells"])

    def test_range_one_sees_only_adjacent(self):
        sys = PerceptionSystem()
        w = _empty_world()
        result = sys.observe(w, (4, 4), body_state=_body(1))
        for cell in result["visible_cells"]:
            assert cell["distance"] <= 1

    def test_range_max_sees_far_cells(self):
        sys = PerceptionSystem()
        w = _empty_world()
        result = sys.observe(w, (4, 4), body_state=_body(7))
        assert result["vision_range"] == 7

    def test_body_none_uses_default(self):
        sys = PerceptionSystem()
        w = _empty_world()
        result = sys.observe(w, (0, 0), body_state=None)
        assert result["vision_range"] == DEFAULT_VISION_RANGE

    def test_body_without_vision_range_attr_uses_param(self):
        sys = PerceptionSystem()
        w = _empty_world()
        bs_no_vr = types.SimpleNamespace()
        result = sys.observe(w, (0, 0), vision_range=2, body_state=bs_no_vr)
        assert result["vision_range"] == 2

    @pytest.mark.parametrize("vr", [1, 2, 3, 4, 5])
    def test_vision_range_in_result(self, vr):
        sys = PerceptionSystem()
        w = _empty_world()
        result = sys.observe(w, (4, 4), body_state=_body(vr))
        assert result["vision_range"] == vr
