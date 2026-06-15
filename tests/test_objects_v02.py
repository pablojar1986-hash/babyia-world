"""Tests de GridWorld con objetos 0.2."""
import numpy as np
from world.grid_world import GridWorld
from world.inventory import Inventory
from world.objects import Cell, STATE_SIZE


# ── Observacion ───────────────────────────────────────────────────────────────

def test_reset_returns_10_features():
    """El mundo base devuelve 10 features (sin inventario)."""
    w = GridWorld()
    obs = w.reset()
    assert obs.shape == (10,)


def test_state_size_constant():
    assert STATE_SIZE == 18


# ── Puerta cerrada sin llave ──────────────────────────────────────────────────

def test_door_blocks_without_key():
    w = GridWorld()
    w.reset()
    # Muevo a BabyIA a (2,6) manualmente y luego intento entrar en (3,6)=DOOR
    w.baby_pos = [2, 6]
    _, _, _, info = w.step(3, has_key=False)  # RIGHT hacia (3,6)
    assert info["hit_wall"] is True or info["hit_door_closed"] is True
    assert tuple(w.baby_pos) == (2, 6)  # no se movio


def test_door_passable_with_key():
    w = GridWorld()
    w.reset()
    w.baby_pos = [2, 6]
    obs, _, _, info = w.step(3, has_key=True)  # RIGHT hacia (3,6)
    assert info["opened_door"] is True
    assert w.door_open is True
    assert tuple(w.baby_pos) == (3, 6)


# ── Llave ─────────────────────────────────────────────────────────────────────

def test_key_collected_when_entered():
    w = GridWorld()
    w.reset()
    w.baby_pos = [0, 6]
    assert w.key_present is True
    _, _, _, info = w.step(3, has_key=False)  # RIGHT hacia (1,6)=KEY
    assert info["picked_key"] is True
    assert w.key_present is False


def test_key_not_picked_if_cell_empty():
    w = GridWorld()
    w.reset()
    # Ir a celda vacia (1,0)
    w.baby_pos = [0, 0]
    _, _, _, info = w.step(3)  # RIGHT hacia (1,0)
    assert info.get("picked_key", False) is False


# ── Comida ────────────────────────────────────────────────────────────────────

def test_food_collected_when_entered():
    w = GridWorld()
    w.reset()
    w.baby_pos = [5, 2]
    assert w.food_present is True
    _, _, _, info = w.step(3)  # RIGHT hacia (6,2)=FOOD
    assert info["ate_food"] is True
    assert w.food_present is False


# ── Peligro ───────────────────────────────────────────────────────────────────

def test_danger_passable():
    w = GridWorld()
    w.reset()
    w.baby_pos = [2, 5]
    _, _, _, info = w.step(3)  # RIGHT hacia (3,5)=DANGER
    assert info["in_danger"] is True
    assert tuple(w.baby_pos) == (3, 5)  # se mueve, no bloquea


# ── Objeto desconocido ────────────────────────────────────────────────────────

def test_unknown_found_first_time():
    w = GridWorld()
    w.reset()
    w.baby_pos = [6, 1]
    _, _, _, info = w.step(3)  # RIGHT hacia (7,1)=UNKNOWN
    assert info["found_unknown"] is True
    assert w.unknown_touched is True


def test_unknown_not_repeated():
    w = GridWorld()
    w.reset()
    w.baby_pos = [6, 1]
    w.step(3)  # entra en (7,1)
    # Salir y volver
    w.step(2)  # vuelve a (6,1)
    _, _, _, info = w.step(3)  # vuelve a (7,1)
    assert info.get("found_unknown", False) is False


# ── get_grid ──────────────────────────────────────────────────────────────────

def test_get_grid_shows_key():
    w = GridWorld()
    w.reset()
    grid = w.get_grid()
    assert grid[6][1] == int(Cell.KEY)


def test_get_grid_shows_door_closed():
    w = GridWorld()
    w.reset()
    grid = w.get_grid()
    assert grid[6][3] == int(Cell.DOOR_CLOSED)


def test_get_grid_door_open_after_opening():
    w = GridWorld()
    w.reset()
    w.baby_pos = [2, 6]
    w.step(3, has_key=True)  # abre puerta
    grid = w.get_grid()
    assert grid[6][3] == int(Cell.DOOR_OPEN)


# ── Compatibilidad con 0.1.x ──────────────────────────────────────────────────

def test_reached_goal_still_works():
    w = GridWorld()
    w.reset()
    w.baby_pos = [6, 7]
    _, _, done, info = w.step(3)  # RIGHT hacia (7,7)=GOAL
    assert info["reached_goal"] is True
    assert done is True


def test_hit_wall_still_works():
    w = GridWorld()
    w.reset()
    # (2,0) es pared
    w.baby_pos = [1, 0]
    _, _, _, info = w.step(3)  # RIGHT hacia (2,0)=WALL
    assert info["hit_wall"] is True
