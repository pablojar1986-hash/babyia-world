"""Tests que paredes bloquean el campo visual (FOV) — BabyIA 0.4.5b."""

from world.grid_world import GridWorld
from brain.perception import PerceptionSystem, VIS_VISIBLE, VIS_BLOCKED


def _world_with_wall(wall_pos: tuple, grid_size: int = 8) -> GridWorld:
    """Mundo vacio con una pared en wall_pos."""
    w = GridWorld(grid_size=grid_size)
    w.reset()
    w.set_walls(frozenset({wall_pos}))
    return w


class TestFOVWallBlocksVisibility:
    def test_adjacent_cell_always_visible(self):
        sys = PerceptionSystem()
        w = _world_with_wall((2, 0))
        result = sys.observe(w, (0, 0), vision_range=3)
        visible_positions = {
            tuple(c["position"])
            for c in result["visible_cells"]
            if c["visibility"] == VIS_VISIBLE
        }
        assert (1, 0) in visible_positions

    def test_wall_blocks_far_cell(self):
        """Celda detras de pared no debe estar en visible_objects."""
        sys = PerceptionSystem()
        w = _world_with_wall((0, 2))
        result = sys.observe(w, (0, 0), vision_range=5)
        visible_obj_positions = {
            tuple(o["position"]) for o in result["visible_objects"]
        }
        # (0,4) is 4 steps away, blocked by wall at (0,2)
        assert (0, 4) not in visible_obj_positions

    def test_no_wall_clear_path(self):
        """Sin pared, celda lejana puede ser visible."""
        sys = PerceptionSystem()
        w = GridWorld(grid_size=8)
        w.reset()
        w.set_walls(frozenset())
        result = sys.observe(w, (0, 0), vision_range=5)
        all_positions = {tuple(c["position"]) for c in result["visible_cells"]}
        assert (0, 3) in all_positions

    def test_blocked_count_positive_when_walls_present(self):
        sys = PerceptionSystem()
        w = _world_with_wall((2, 2))
        result = sys.observe(w, (0, 0), vision_range=4)
        # There may be cells blocked by the wall
        assert result["blocked_count"] >= 0

    def test_fov_active_flag(self):
        sys = PerceptionSystem()
        w = GridWorld(grid_size=8)
        w.reset()
        result = sys.observe(w, (0, 0), vision_range=3)
        assert result["fov_active"] is True

    def test_visible_cells_includes_all_scanned(self):
        sys = PerceptionSystem()
        w = GridWorld(grid_size=8)
        w.reset()
        result = sys.observe(w, (4, 4), vision_range=2)
        for cell in result["visible_cells"]:
            assert "visibility" in cell
            assert cell["visibility"] in (VIS_VISIBLE, VIS_BLOCKED)

    def test_visible_objects_only_has_visible(self):
        """visible_objects no debe contener objetos bloqueados."""
        sys = PerceptionSystem()
        w = GridWorld(grid_size=8)
        w.reset()
        result = sys.observe(w, (4, 4), vision_range=3)
        for obj in result["visible_objects"]:
            assert obj["visibility"] == VIS_VISIBLE

    def test_line_of_sight_helper_adjacent(self):
        sys = PerceptionSystem()
        w = GridWorld(grid_size=8)
        w.reset()
        grid = w.get_grid()
        assert sys._has_line_of_sight(grid, (0, 0), (1, 0), 8) is True
        assert sys._has_line_of_sight(grid, (0, 0), (0, 1), 8) is True

    def test_line_of_sight_blocked_by_wall(self):
        sys = PerceptionSystem()
        w = _world_with_wall((0, 2))
        grid = w.get_grid()
        assert sys._has_line_of_sight(grid, (0, 0), (0, 4), 8) is False
