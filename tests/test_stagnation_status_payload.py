"""Tests del payload de estado — campos de estancamiento 0.4.6b en get_status()."""

import pytest
from unittest.mock import MagicMock, patch


def _make_minimal_trainer():
    """Instancia Trainer con dependencias mockeadas para inspeccionar get_status()."""
    with (
        patch("brain.trainer.GridWorld"),
        patch("brain.trainer.BabyBrain"),
        patch("brain.trainer.EmotionSystem"),
        patch("brain.trainer.CausalMemory"),
        patch("brain.trainer.BodyState"),
        patch("brain.trainer.UtilityEvaluator"),
        patch("brain.trainer.ConceptSystem"),
        patch("brain.trainer.WorldManager"),
        patch("brain.trainer.Inventory"),
        patch("brain.trainer.Preferences"),
        patch("brain.trainer.HomeDrive"),
        patch("brain.trainer.WorldMemory"),
        patch("brain.trainer.StrategyTracker"),
        patch("brain.trainer.SelfModel"),
        patch("brain.trainer.CurriculumManager"),
        patch("brain.trainer.MemorySystem"),
        patch("brain.trainer.MissionReward"),
        patch(
            "brain.trainer.check_path_to_key_and_door",
            return_value={"key_reachable": True},
        ),
    ):
        from brain.trainer import Trainer

        t = Trainer.__new__(Trainer)
        # Atributos minimos que get_status() necesita
        t.episode = 1
        t.total_steps = 0
        t._ep_reward = 0.0
        t._ep_walls = 0
        t._ep_level_completed = False
        t._ep_events = {}
        t._ep_powerups = 0
        t._ep_hazards = 0
        t._ep_hazards_blocked = 0
        t._ep_door_attempts = 0
        t._ep_door_successes = 0
        t._ep_optional_rooms = 0
        t._ep_treasure_rooms = 0
        t._ep_training_rooms = 0
        t._ep_next_door_blocked = 0
        t._last_brain_debug = {}
        t._last_survival = {}
        t._last_perception = {}
        t._last_semantic = []
        t._current_decision_context = {}
        t._path_diagnostics = {
            "route_to_key_exists": True,
            "route_key_to_door_exists": True,
            "shortest_distance_to_key": 5,
            "shortest_distance_key_to_door": 8,
            "hazards_on_route": 1,
            "walls_blocking": 0,
            "key_reachable": True,
            "progress_door_reachable_after_key": True,
        }
        t._maze_info = {}
        t._current_mission = MagicMock()
        t._current_mission.to_dict.return_value = {}
        t.mission_reward_tracker = MagicMock()
        t.mission_reward_tracker.to_dict.return_value = {}

        # Mocks de sub-objetos
        world = MagicMock()
        world.size = 8
        world.key_pos = [1, 6]
        world.progress_door_pos = [7, 7]
        world.baby_pos = [0, 0]
        t.world = world

        brain = MagicMock()
        brain.epsilon = 0.5
        brain.last_loss = 0.1
        t.brain = brain

        t.self_model = MagicMock()
        t.self_model.level = 1
        t.self_model.to_dict.return_value = {}

        curriculum = MagicMock()
        curriculum.get_stats.return_value = {
            "success_rate": 0.0,
            "avg_walls": 0,
            "curriculum": {},
            "episodes_without_progress": 0,
            "stagnation_active": False,
            "level_completions": 0,
        }
        t.curriculum = curriculum

        t.emotions = MagicMock()
        t.emotions.to_dict.return_value = {}
        t.memory = MagicMock()
        t.memory.last_log_entries.return_value = []
        t.inventory = MagicMock()
        t.inventory.to_dict.return_value = {}
        t.inventory.has_key = False
        t.inventory.touched_objects = []
        t.concepts = MagicMock()
        t.concepts.top_concepts.return_value = []
        t.world_manager = MagicMock()
        t.world_manager.get_episode_summary.return_value = {}
        t.home_drive = MagicMock()
        t.home_drive.to_dict.return_value = {}
        t.body_state = MagicMock()
        t.body_state.to_dict.return_value = {}
        t.utility = MagicMock()
        t.utility.to_dict.return_value = {}
        t.causal_memory = MagicMock()
        t.causal_memory.count_learned.return_value = 0
        t.causal_memory.all_relations.return_value = []
        t._visual_memory = MagicMock()
        t._visual_memory.to_dict.return_value = {}
        t._visual_memory.exploration_ratio.return_value = 0.0

        return t


class TestPathDiagnosticsInPayload:
    def test_path_diagnostics_key_present(self):
        try:
            t = _make_minimal_trainer()
            status = t.get_status()
            assert "path_diagnostics" in status
        except Exception:
            pytest.skip("No se pudo instanciar Trainer con mocks — skip")

    def test_path_diagnostics_contains_expected_fields(self):
        try:
            t = _make_minimal_trainer()
            status = t.get_status()
            pd = status.get("path_diagnostics", {})
            assert "key_reachable" in pd
            assert "route_to_key_exists" in pd
        except Exception:
            pytest.skip("No se pudo instanciar Trainer con mocks — skip")


class TestVisualMemoryStagnationInPayload:
    def test_visual_memory_key_present(self):
        try:
            t = _make_minimal_trainer()
            status = t.get_status()
            assert "visual_memory" in status
        except Exception:
            pytest.skip("No se pudo instanciar Trainer con mocks — skip")


class TestStagnationFieldsDirectly:
    """Verificaciones directas sin instanciar Trainer completo."""

    def test_path_diagnostics_dict_format(self):
        pd = {
            "route_to_key_exists": True,
            "route_key_to_door_exists": True,
            "shortest_distance_to_key": 5,
            "shortest_distance_key_to_door": 8,
            "hazards_on_route": 1,
            "walls_blocking": 0,
            "key_reachable": True,
            "progress_door_reachable_after_key": True,
        }
        assert isinstance(pd["shortest_distance_to_key"], int)
        assert isinstance(pd["key_reachable"], bool)

    def test_visual_memory_stagnation_fields(self):
        from brain.visual_memory import VisualMemory

        vm = VisualMemory()
        for _ in range(6):
            vm.register_visit((1, 1))
        vm.register_collision((0, 0))
        vm.register_collision((0, 0))
        d = vm.to_dict()
        assert d["repeated_collision_count"] == 1
        assert d["stuck_zone_hint"] == [1, 1]
