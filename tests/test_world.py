import numpy as np
import pytest
from world.grid_world import GridWorld, MAX_STEPS, GOAL_POS, START_POS
from world.objects import Action


@pytest.fixture
def world():
    return GridWorld()


def test_reset_returns_valid_observation(world):
    obs = world.reset()
    assert isinstance(obs, np.ndarray)
    assert obs.shape == (10,)
    assert world.baby_pos == list(START_POS)


def test_move_right_from_start(world):
    world.reset()
    _, _, _, info = world.step(Action.RIGHT)
    assert world.baby_pos == [1, 0]
    assert not info["hit_wall"]


def test_wall_collision_at_boundary(world):
    world.reset()
    # Mover arriba desde (0,0) → fuera de límites
    _, reward, _, info = world.step(Action.UP)
    assert info["hit_wall"]
    assert reward < 0
    assert world.baby_pos == [0, 0]  # posición no cambia


def test_new_cell_gives_bonus(world):
    world.reset()
    _, reward, _, info = world.step(Action.RIGHT)
    assert info["visited_new"]
    assert reward > -0.05  # recibe bono por celda nueva


def test_goal_reached(world):
    # 0.4.3: (7,7) es NEXT_LEVEL_DOOR — requiere llave para completar
    world.reset()
    world.baby_pos = [GOAL_POS[0] - 1, GOAL_POS[1]]
    _, reward, done, info = world.step(Action.RIGHT, has_key=True)
    assert info["reached_goal"]
    assert info["level_completed"]
    assert done
    assert reward > 0  # recompensa de level_completed supera penalizacion de paso


def test_step_limit(world):
    world.reset()
    done = False
    for _ in range(MAX_STEPS):
        _, _, done, _ = world.step(Action.WAIT)
    assert done


def test_observation_values_in_range(world):
    obs = world.reset()
    assert all(-1.0 <= v <= 2.0 for v in obs), "Observación fuera de rango esperado"


def test_visited_cells_tracked(world):
    world.reset()
    initial = len(world.visited)
    world.step(Action.RIGHT)
    assert len(world.visited) == initial + 1
