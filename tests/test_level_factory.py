"""Tests para world/level_factory.py."""
from world.level_factory import (
    get_maze_for_level, save_level_stats, load_level_stats, BASE_WALLS,
)


def test_get_maze_returns_dict():
    assert isinstance(get_maze_for_level(0), dict)


def test_get_maze_required_keys():
    info = get_maze_for_level(1)
    for key in ("level", "walls", "seed", "density", "difficulty",
                "solvable", "description", "wall_count"):
        assert key in info, f"Falta clave: {key}"


def test_level_0_uses_base_walls():
    assert get_maze_for_level(0)["walls"] == BASE_WALLS


def test_level_1_uses_base_walls():
    assert get_maze_for_level(1)["walls"] == BASE_WALLS


def test_level_2_differs_from_base():
    assert get_maze_for_level(2)["walls"] != BASE_WALLS


def test_all_levels_solvable():
    for level in range(7):
        info = get_maze_for_level(level)
        assert info["solvable"] is True, f"Nivel {level} no solucionable"


def test_wall_count_nondecreasing_from_2():
    counts = [get_maze_for_level(lv)["wall_count"] for lv in range(2, 7)]
    assert all(counts[i] <= counts[i + 1] for i in range(len(counts) - 1))


def test_difficulty_labels_are_strings():
    for level in range(7):
        diff = get_maze_for_level(level)["difficulty"]
        assert isinstance(diff, str) and len(diff) > 0


def test_walls_is_frozenset():
    for level in range(7):
        assert isinstance(get_maze_for_level(level)["walls"], frozenset)


def test_clamp_below_0():
    info = get_maze_for_level(-1)
    assert info["level"] == 0


def test_clamp_above_6():
    info = get_maze_for_level(99)
    assert info["level"] == 6


def test_wall_count_matches_walls():
    for level in range(7):
        info = get_maze_for_level(level)
        assert info["wall_count"] == len(info["walls"])


def test_save_creates_file(tmp_path):
    p = tmp_path / "lvl.json"
    save_level_stats(get_maze_for_level(2), stats_file=p)
    assert p.exists()


def test_save_and_load_roundtrip(tmp_path):
    p = tmp_path / "lvl.json"
    maze = get_maze_for_level(3)
    save_level_stats(maze, stats_file=p)
    loaded = load_level_stats(stats_file=p)
    assert loaded["level"] == 3
    assert loaded["difficulty"] == maze["difficulty"]
    assert loaded["solvable"] is True


def test_load_missing_returns_empty(tmp_path):
    assert load_level_stats(stats_file=tmp_path / "nonexistent.json") == {}
