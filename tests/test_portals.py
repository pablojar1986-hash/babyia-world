"""Tests de Portal y HOME_PORTALS."""
import pytest

from worlds.portal import Portal
from worlds.world_registry import (
    ALL_WORLDS, HOME_PORTALS, RETURN_HOME_PORTAL, HOME_WORLD_ID,
    FOOD_WORLD_ID, DANGER_WORLD_ID, CURIOSITY_WORLD_ID, CHALLENGE_WORLD_ID,
)


def test_portal_creation():
    p = Portal("test", "food_world", "Test", 0, (5, 3), (100, 100, 100))
    assert p.portal_id    == "test"
    assert p.target_world == "food_world"
    assert p.position     == (5, 3)
    assert p.is_unlocked  is True


def test_portal_can_enter_when_level_met():
    p = Portal("p", "x", "X", required_level=2, position=(1, 1), color=(0, 0, 0))
    assert p.can_enter(2) is True
    assert p.can_enter(3) is True


def test_portal_cannot_enter_when_level_insufficient():
    p = Portal("p", "x", "X", required_level=2, position=(1, 1), color=(0, 0, 0))
    assert p.can_enter(0) is False
    assert p.can_enter(1) is False


def test_portal_locked_blocks_entry():
    p = Portal("p", "x", "X", required_level=0, position=(1, 1),
               color=(0, 0, 0), is_unlocked=False)
    assert p.can_enter(5) is False


def test_home_portals_exist_and_have_unique_positions():
    assert len(HOME_PORTALS) == 4
    positions = [p.position for p in HOME_PORTALS.values()]
    assert len(set(positions)) == 4, "Portales deben tener posiciones unicas"


def test_portal_target_worlds_exist():
    for portal in HOME_PORTALS.values():
        assert portal.target_world in ALL_WORLDS, (
            f"Portal {portal.portal_id} apunta a mundo desconocido: {portal.target_world}"
        )


def test_portal_positions_not_wall():
    from world.level_factory import BASE_WALLS
    for portal in HOME_PORTALS.values():
        assert portal.position not in BASE_WALLS, (
            f"Portal {portal.portal_id} esta en una pared: {portal.position}"
        )


def test_return_home_portal_target():
    assert RETURN_HOME_PORTAL.target_world == HOME_WORLD_ID
    assert RETURN_HOME_PORTAL.required_level == 0


def test_portal_to_dict():
    p = HOME_PORTALS["blue_door"]
    d = p.to_dict()
    assert d["portal_id"]    == "blue_door"
    assert d["target_world"] == FOOD_WORLD_ID
    assert isinstance(d["position"], list)


def test_all_worlds_have_reward_profiles():
    from worlds.reward_profiles import REWARD_PROFILES
    for world in ALL_WORLDS.values():
        assert world.reward_profile in REWARD_PROFILES, (
            f"Mundo {world.world_id} tiene perfil desconocido: {world.reward_profile}"
        )
