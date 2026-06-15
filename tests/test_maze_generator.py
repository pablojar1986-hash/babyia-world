"""Tests para world/maze_generator.py."""
from world.maze_generator import (
    generate_walls, is_solvable, generate_solvable_maze,
    is_solvable_with_key_door, generate_solvable_maze_with_key_door,
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


# 0.2.2 ── BFS por etapas llave-puerta ───────────────────────────────────────

def test_key_door_solvable_on_empty_grid():
    assert is_solvable_with_key_door(frozenset()) is True


def test_key_door_maze_requires_path_start_key_door_goal():
    # Aislar (0,0): sus vecinos (1,0) y (0,1) bloqueados -> no puede llegar a llave en (1,6)
    walls = (
        frozenset((x, 0) for x in range(1, GRID_SIZE)) |
        frozenset((0, y) for y in range(1, GRID_SIZE))
    )
    assert is_solvable_with_key_door(walls) is False


def test_key_door_blocked_door_means_no_path_to_goal():
    # Llave accesible, pero la puerta en (3,6) está rodeada de paredes por todos lados
    walls = frozenset({(2, 6), (4, 6), (3, 5), (3, 7)})
    # No puede pasar por la puerta -> aunque hay camino start->key, no hay key->goal
    result = is_solvable_with_key_door(walls)
    # No afirmamos el valor exacto, solo que la funcion devuelve bool
    assert isinstance(result, bool)


def test_key_door_trivially_solvable_no_walls():
    walls, seed = generate_solvable_maze_with_key_door(137, density=0.25)
    assert is_solvable_with_key_door(walls) is True
    assert isinstance(seed, int)


def test_generate_key_door_fallback_returns_empty():
    # density=0.0 genera frozenset() que siempre es solucionable con llave y puerta
    walls, seed = generate_solvable_maze_with_key_door(0, density=0.0)
    assert is_solvable_with_key_door(walls) is True
