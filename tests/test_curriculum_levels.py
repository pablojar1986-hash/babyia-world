"""Tests de integracion Curriculum con sistema de niveles (0.2.1)."""
from brain.curriculum import Curriculum, MAX_LEVEL
from world.level_factory import get_maze_for_level


def test_initial_level_is_0():
    assert Curriculum().current_level == 0


def test_no_level_up_without_enough_episodes():
    c = Curriculum()
    for _ in range(10):
        c.record_episode(True, 0)
    assert c.check_level_up() is None


def test_level_up_to_1_on_success():
    c = Curriculum()
    for _ in range(20):
        c.record_episode(True, 0)
    assert c.check_level_up() == 1
    assert c.current_level == 1


def test_maze_needs_update_set_on_level_up():
    c = Curriculum()
    for _ in range(20):
        c.record_episode(True, 0)
    c.check_level_up()
    assert c.maze_needs_update is True


def test_consume_maze_update_resets_flag():
    c = Curriculum()
    for _ in range(20):
        c.record_episode(True, 0)
    c.check_level_up()
    assert c.consume_maze_update() is True
    assert c.maze_needs_update is False


def test_consume_maze_update_false_if_no_change():
    assert Curriculum().consume_maze_update() is False


def test_max_level_not_exceeded():
    c = Curriculum()
    c.current_level = MAX_LEVEL
    for _ in range(20):
        c.record_episode(True, 0)
    assert c.check_level_up() is None
    assert c.current_level == MAX_LEVEL


def test_level_2_requires_low_walls():
    c = Curriculum()
    c.current_level = 1
    for i in range(20):
        c.record_episode(i % 10 < 8, 5)  # 80% exito, avg_walls=5 > 3.0
    assert c.check_level_up() is None


def test_level_2_passes_with_low_walls():
    c = Curriculum()
    c.current_level = 1
    for _ in range(20):
        c.record_episode(True, 0)
    assert c.check_level_up() == 2


def test_max_level_constant_is_6():
    assert MAX_LEVEL == 6


def test_level_factory_all_levels_solvable():
    for level in range(MAX_LEVEL + 1):
        maze = get_maze_for_level(level)
        assert maze["solvable"] is True, f"Nivel {level} no solucionable"
        assert maze["level"] == level


def test_get_stats_initial():
    stats = Curriculum().get_stats()
    assert stats["success_rate"] == 0.0
    assert stats["avg_walls"] == 0.0
