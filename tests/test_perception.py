"""Tests para brain/perception.py — BabyIA 0.4.5."""

from world.grid_world import GridWorld
from brain.perception import PerceptionSystem


def _make_world(gs=8):
    w = GridWorld(grid_size=gs)
    w.reset()
    return w


class TestPerceptionObserve:
    def test_returns_dict(self):
        p = PerceptionSystem()
        w = _make_world()
        result = p.observe(w, (0, 0))
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        p = PerceptionSystem()
        w = _make_world()
        result = p.observe(w, (0, 0))
        for key in (
            "vision_range",
            "visible_cells",
            "visible_objects",
            "nearest_key",
            "nearest_hazard",
            "danger_count",
            "reward_count",
            "total_visible",
        ):
            assert key in result, f"Missing key: {key}"

    def test_vision_range_matches_param(self):
        p = PerceptionSystem()
        w = _make_world()
        result = p.observe(w, (0, 0), vision_range=2)
        assert result["vision_range"] == 2

    def test_no_visible_objects_at_start_far_from_all(self):
        p = PerceptionSystem()
        w = _make_world()
        # En (0,0) con vision_range=1 no deberia ver KEY en (1,6)
        result = p.observe(w, (0, 0), vision_range=1)
        assert result["nearest_key"] is None

    def test_sees_key_when_adjacent(self):
        p = PerceptionSystem()
        w = _make_world()
        kx, ky = w.key_pos
        # Posicionarse un paso a la derecha de la llave
        result = p.observe(w, (kx - 1, ky), vision_range=2)
        assert result["nearest_key"] is not None

    def test_danger_count_positive_near_danger(self):
        p = PerceptionSystem()
        w = _make_world()
        dx, dy = w.danger_pos
        # Cerca del peligro
        result = p.observe(w, (dx - 1, dy), vision_range=3)
        assert result["danger_count"] >= 1

    def test_total_visible_is_non_negative(self):
        p = PerceptionSystem()
        w = _make_world()
        result = p.observe(w, (4, 4), vision_range=3)
        assert result["total_visible"] >= 0

    def test_visible_cells_have_position_and_distance(self):
        p = PerceptionSystem()
        w = _make_world()
        result = p.observe(w, (4, 4), vision_range=2)
        for cell in result["visible_cells"]:
            assert "position" in cell
            assert "distance" in cell

    def test_large_grid(self):
        p = PerceptionSystem()
        w = _make_world(gs=16)
        result = p.observe(w, (0, 0), vision_range=3)
        assert result["vision_range"] == 3
        assert result["total_visible"] >= 0

    def test_objects_have_required_fields(self):
        p = PerceptionSystem()
        w = _make_world()
        result = p.observe(w, (4, 4), vision_range=4)
        for obj in result["visible_objects"]:
            assert "kind" in obj
            assert "position" in obj
            assert "distance" in obj
            assert "category" in obj


class TestPerceptionWithNoKey:
    def test_no_key_when_key_picked(self):
        p = PerceptionSystem()
        w = _make_world()
        w.key_present = False
        kx, ky = w.key_pos
        # Incluso al lado de la posicion de la llave, no deberia aparecer
        result = p.observe(w, (kx - 1, ky), vision_range=3)
        assert result["nearest_key"] is None
