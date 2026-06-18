"""Tests del WorldManager: transiciones de mundo, portales y estado."""

from worlds.world_manager import WorldManager, RETURN_SIGNAL_STEPS
from worlds.world_registry import (
    HOME_WORLD_ID,
    FOOD_WORLD_ID,
    HOME_PORTALS,
)


def make_wm() -> WorldManager:
    return WorldManager()


def test_initial_state_is_home():
    wm = make_wm()
    assert wm.current_world_id == HOME_WORLD_ID
    assert wm.is_at_home is True
    assert wm.reward_outside == 0.0


def test_reset_clears_state():
    wm = make_wm()
    wm.current_world_id = FOOD_WORLD_ID
    wm.is_at_home = False
    wm._steps_outside = 10
    wm.reset()
    assert wm.current_world_id == HOME_WORLD_ID
    assert wm.is_at_home is True
    assert wm._steps_outside == 0


def test_enter_portal_food_world():
    wm = make_wm()
    portal = HOME_PORTALS["blue_door"]  # pos (7,2), level 0
    delta, events = wm.process_step(portal.position, player_level=0)
    assert events.get("entered_world") == FOOD_WORLD_ID
    assert wm.is_at_home is False
    assert wm.current_world_id == FOOD_WORLD_ID


def test_cannot_enter_locked_portal_insufficient_level():
    wm = make_wm()
    portal = HOME_PORTALS["red_door"]  # required_level=1
    wm.process_step(portal.position, player_level=0)
    # Nivel 0 no puede entrar a danger_world (nivel minimo 1)
    assert wm.current_world_id == HOME_WORLD_ID
    assert wm.is_at_home is True


def test_return_home_gives_base_reward():
    wm = make_wm()
    # Entrar a food world
    wm.process_step((7, 2), player_level=0)
    assert not wm.is_at_home
    # Regresar a casa sin haber explorado
    delta, events = wm.process_step((0, 0), player_level=0)
    assert events.get("returned_home") is True
    assert delta > 0
    assert wm.is_at_home is True


def test_return_after_explore_gives_bigger_reward():
    from worlds.reward_profiles import REWARD_PROFILES

    wm = make_wm()
    wm.process_step((7, 2), player_level=0)
    # Simular que gano recompensa fuera
    wm._explored = True
    wm.reward_outside = 5.0
    delta, events = wm.process_step((0, 0), player_level=0)
    assert delta >= REWARD_PROFILES["home"]["return_after_explore"]


def test_should_return_home_after_threshold():
    wm = make_wm()
    wm.process_step((7, 2), player_level=0)  # entra a food
    assert not wm.should_return_home()
    wm._steps_outside = RETURN_SIGNAL_STEPS
    assert wm.should_return_home()


def test_get_state_features_shape_and_range():
    wm = make_wm()
    feats = wm.get_state_features((3, 4))
    assert feats.shape == (8,)
    assert all(f >= 0.0 for f in feats), "features must be >= 0"


def test_worlds_visited_tracks_entries():
    wm = make_wm()
    wm.process_step((7, 2), player_level=0)  # food
    assert FOOD_WORLD_ID in wm.worlds_visited


def test_no_direct_world_hop_without_returning_home():
    wm = make_wm()
    # Entrar a food_world
    wm.process_step((7, 2), player_level=1)
    assert wm.current_world_id == FOOD_WORLD_ID
    # Intentar ir a red_door (danger) sin pasar por casa
    red_pos = HOME_PORTALS["red_door"].position
    wm.process_step(red_pos, player_level=2)
    # No debe hacer world-hop desde fuera de casa
    assert wm.current_world_id == FOOD_WORLD_ID
