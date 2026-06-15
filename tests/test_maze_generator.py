"""Tests para world/maze_generator.py."""
from world.maze_generator import (
    generate_walls, is_solvable, generate_solvable_maze,
    GRID_SIZE, _RESERVED,
)


def test_generate_walls_returns_frozenset():
    assert isinstance(generate_walls(42), frozenset)


def test_walls_within_grid():
    for x, y in generate_walls(42):
        assert 0 <= x < GRID_SIZE
        assert 0 <= y < GRID_SIZE


def test_reserved_positions_not_walls():
    walls = generate_walls(42)
    assert not (walls & _RESERVED), "Posiciones reservadas no deben ser paredes"


def test_is_solvable_empty_grid():
    assert is_solvable(frozenset()) is True


def test_is_solvable_blocked_start():
    # Bloquear todos los vecinos de (0,0) para aislar el inicio
    walls = (
        frozenset((x, 0) for x in range(1, GRID_SIZE)) |
        frozenset((0, y) for y in range(1, GRID_SIZE))
    )
    assert is_solvable(walls) is False


def test_generate_solvable_returns_solvable():
    walls, _seed = generate_solvable_maze(42, density=0.20)
    assert is_solvable(walls) is True


def test_generate_solvable_returns_int_seed():
    _walls, seed = generate_solvable_maze(99)
    assert isinstance(seed, int)


def test_density_affects_wall_count():
    low  = generate_walls(42, density=0.10)
    high = generate_walls(42, density=0.30)
    assert len(high) > len(low)


def test_same_seed_deterministic():
    assert generate_walls(77) == generate_walls(77)


def test_fallback_on_impossible_density():
    # Densidad 0.0 siempre genera frozenset vacio, que es solucionable
    walls, seed = generate_solvable_maze(0, density=0.0)
    assert is_solvable(walls) is True


def test_generate_multiple_levels_all_solvable():
    seeds = [42, 99, 137, 256, 512]
    densities = [0.15, 0.20, 0.25, 0.30, 0.35]
    for s, d in zip(seeds, densities):
        walls, _ = generate_solvable_maze(s, density=d)
        assert is_solvable(walls), f"seed={s}, density={d} no solucionable"
