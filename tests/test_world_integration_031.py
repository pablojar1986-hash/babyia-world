"""
Tests de integracion 0.3.1: verifica que _apply_interactions llama
a world_manager.on_object_event() y que end_episode aplica penalizacion
fuera de casa.
"""
import numpy as np
import pytest

from worlds.world_manager import WorldManager
from worlds.world_registry import FOOD_WORLD_ID
from worlds.reward_profiles import REWARD_PROFILES, EPISODE_END_OUTSIDE_HOME


# ── on_object_event aplica perfil de mundo ────────────────────────────────────

def test_eat_food_bonus_in_food_world():
    wm = WorldManager()
    # Entrar a food_world (nivel 0 suficiente)
    wm.process_step((7, 2), player_level=0)
    assert wm.current_world_id == FOOD_WORLD_ID
    # Comer comida en food_world da bonus
    delta = wm.on_object_event("ate_food")
    assert delta == REWARD_PROFILES["food"]["eat_food"]


def test_eat_food_bonus_in_home():
    wm = WorldManager()
    # En casa, comer comida no da bonus de perfil (perfil home no tiene eat_food)
    delta = wm.on_object_event("ate_food")
    assert delta == 0.0


def test_danger_penalty_higher_in_danger_world():
    wm = WorldManager()
    # Entrar a danger_world (nivel 1)
    wm.process_step((7, 4), player_level=1)
    delta_danger_world = wm.on_object_event("in_danger")
    wm2 = WorldManager()
    delta_home = wm2.on_object_event("in_danger")
    # En danger_world hay penalizacion; en casa no
    assert delta_danger_world < 0
    assert delta_home == 0.0


def test_discover_unknown_bonus_in_curiosity_world():
    wm = WorldManager()
    wm.process_step((7, 6), player_level=2)   # green_door → curiosity
    delta = wm.on_object_event("found_unknown")
    assert delta == REWARD_PROFILES["curiosity"]["discover_unknown"]


def test_on_object_event_tracks_reward_outside():
    wm = WorldManager()
    wm.process_step((7, 2), player_level=0)    # food_world
    assert wm.reward_outside == 0.0
    wm.on_object_event("ate_food")
    assert wm.reward_outside > 0.0


# ── on_episode_end penaliza si fuera de casa ─────────────────────────────────

def test_episode_end_at_home_no_penalty():
    wm = WorldManager()
    assert wm.is_at_home is True
    penalty = wm.on_episode_end()
    assert penalty == 0.0


def test_episode_end_outside_home_penalty():
    wm = WorldManager()
    wm.process_step((7, 2), player_level=0)
    assert not wm.is_at_home
    penalty = wm.on_episode_end()
    assert penalty == EPISODE_END_OUTSIDE_HOME
    assert penalty < 0


def test_trainer_applies_world_object_event(tmp_path):
    """Verifica que Trainer._apply_interactions llama on_object_event."""
    from brain.trainer import Trainer
    t = Trainer(training=False)
    t.start_episode()
    # Forzar BabyIA en food_world
    t.world_manager.current_world_id = FOOD_WORLD_ID
    t.world_manager.is_at_home = False
    # Simular info de comida
    reward_before = t._ep_reward
    info = {
        "hit_wall": False, "reached_goal": False,
        "picked_key": False, "opened_door": False,
        "hit_door_closed": False, "ate_food": True,
        "in_danger": False, "found_unknown": False,
    }
    delta = t._apply_interactions(info)
    # delta debe incluir bonus de food_world
    assert delta > 0, "Comer en food_world debe dar recompensa positiva"


def test_trainer_applies_episode_end_penalty(tmp_path):
    """Verifica que Trainer.end_episode aplica penalizacion si fuera de casa."""
    from brain.trainer import Trainer
    t = Trainer(training=False)
    t.start_episode()
    # Simular que BabyIA termino fuera de casa
    t.world_manager.current_world_id = FOOD_WORLD_ID
    t.world_manager.is_at_home = False
    reward_before = t._ep_reward
    t.end_episode(reached_goal=False)
    # _ep_reward debe haber decrementado por la penalizacion
    assert t._ep_reward < reward_before + 0.01, (
        "end_episode debe aplicar penalizacion por terminar fuera de casa"
    )
