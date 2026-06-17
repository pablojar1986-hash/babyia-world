"""Tests 0.4.3: correcciones de deadlocks de progresion de nivel.

Cubre:
- nivel 0 usa mapa abierto (level_factory, frozenset vacio)
- llave NO se consume al abrir puerta normal -> disponible para next_level_door
- next_level_door bloqueada sin llave / abierta con llave
- level_completed sube curriculum de nivel 0 a 1
- status refleja episodes_without_progress correcto DESPUES de end_episode
- metricas registran level_completed correctamente
"""

from brain.metrics import TrainingMetrics
from brain.trainer import Trainer
from world.grid_world import GridWorld
from world.level_factory import get_maze_for_level


def _make_trainer() -> Trainer:
    t = Trainer(training=False)
    t.start_episode()
    return t


class TestLevel0OpenMap:
    def test_level_factory_nivel0_paredes_vacias(self):
        maze = get_maze_for_level(0)
        assert len(maze["walls"]) == 0

    def test_level_factory_nivel0_dificultad_tutorial(self):
        maze = get_maze_for_level(0)
        assert maze["difficulty"] == "Tutorial"

    def test_trainer_inicia_con_mapa_abierto(self):
        t = Trainer(training=False)
        assert len(t.world.walls) == 0, "nivel 0 debe ser mapa sin paredes"

    def test_maze_info_refleja_nivel0(self):
        t = Trainer(training=False)
        assert t._maze_info["level"] == 0
        assert t._maze_info["difficulty"] == "Tutorial"


class TestKeyNotConsumedByNormalDoor:
    def test_abrir_puerta_normal_mantiene_llave(self):
        t = _make_trainer()
        t.inventory.pick_key()
        assert t.inventory.has_key is True
        t._apply_interactions({"opened_door": True})
        assert (
            t.inventory.has_key is True
        ), "llave debe conservarse tras abrir puerta normal"

    def test_next_level_door_accesible_tras_abrir_puerta_normal(self):
        t = _make_trainer()
        t.inventory.pick_key()
        t._apply_interactions({"opened_door": True})
        # Con llave todavia disponible, puede completar el nivel
        delta = t._apply_interactions(
            {"level_completed": True, "next_level_door_opened": True}
        )
        assert delta > 0
        assert t._ep_level_completed is True


class TestNextLevelDoor:
    def test_next_level_door_sin_llave_bloqueada(self):
        world = GridWorld()
        world.reset()
        world.baby_pos = [6, 7]
        _, _, done, info = world.step(3, has_key=False)  # RIGHT -> (7,7)
        assert info.get("hit_next_level_door") is True
        assert info.get("level_completed") is False
        assert done is False

    def test_next_level_door_con_llave_completa_nivel(self):
        world = GridWorld()
        world.reset()
        world.baby_pos = [6, 7]
        _, _, done, info = world.step(3, has_key=True)  # RIGHT -> (7,7)
        assert info.get("level_completed") is True
        assert done is True


class TestLevelUpFromCompleted:
    def test_level_completed_sube_curriculum_0_a_1(self):
        t = Trainer(training=False)
        t.start_episode()
        t.curriculum.record_episode(False, 0, level_completed=True)
        new_level = t.curriculum.check_level_up()
        assert new_level == 1

    def test_reached_goal_solo_no_sube_nivel(self):
        t = Trainer(training=False)
        for _ in range(20):
            t.start_episode()
            t.curriculum.record_episode(True, 0, level_completed=False)
        new_level = t.curriculum.check_level_up()
        assert new_level is None, "reached_goal solo no debe subir de nivel"


class TestStatusAfterEndEpisode:
    def test_episodes_without_progress_incrementa_tras_end_episode(self):
        t = Trainer(training=False)
        t.start_episode()
        t.end_episode(False, level_completed=False)
        s = t.get_status()
        assert s["episodes_without_progress"] == 1

    def test_episodes_without_progress_se_resetea_con_level_completed(self):
        t = Trainer(training=False)
        t.start_episode()
        t.end_episode(False, level_completed=False)
        t.start_episode()
        t.end_episode(False, level_completed=True)
        s = t.get_status()
        assert s["episodes_without_progress"] == 0


class TestMetricsLevelCompleted:
    def test_metrics_registra_level_completed(self):
        m = TrainingMetrics()
        m.record_episode(
            reached_goal=False,
            reward=120.0,
            steps=50,
            wall_hits=2,
            epsilon=0.5,
            level=0,
            level_completed=True,
        )
        assert m.level_completed_count == 1

    def test_metrics_no_incrementa_sin_level_completed(self):
        m = TrainingMetrics()
        m.record_episode(
            reached_goal=False,
            reward=5.0,
            steps=200,
            wall_hits=10,
            epsilon=0.5,
            level=0,
            level_completed=False,
        )
        assert m.level_completed_count == 0
