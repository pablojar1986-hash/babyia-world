import pytest
from brain.metrics import TrainingMetrics


@pytest.fixture
def metrics(tmp_path):
    return TrainingMetrics(stats_file=tmp_path / "stats.json")


def test_initial_state(metrics):
    assert metrics.total_episodes == 0
    assert metrics.recent_success_rate == 0.0
    assert metrics.best_success_rate == 0.0


def test_record_goal_reached(metrics):
    metrics.record_episode(True, 9.5, 30, 2, 0.5, 1)
    assert metrics.total_episodes == 1
    assert metrics.goal_reached_count == 1
    assert metrics.recent_success_rate == 1.0


def test_record_failure(metrics):
    metrics.record_episode(False, -5.0, 200, 20, 0.9, 0)
    assert metrics.total_episodes == 1
    assert metrics.recent_success_rate == 0.0


def test_best_success_rate_updates(metrics):
    for _ in range(20):
        metrics.record_episode(True, 9.0, 25, 1, 0.3, 1)
    assert metrics.best_success_rate == 1.0


def test_best_rate_not_downgraded(metrics):
    for _ in range(20):
        metrics.record_episode(True, 9.0, 25, 1, 0.3, 1)
    best = metrics.best_success_rate
    for _ in range(20):
        metrics.record_episode(False, -5.0, 200, 20, 0.5, 0)
    assert metrics.best_success_rate == best  # no bajó


def test_average_reward(metrics):
    metrics.record_episode(False, -2.0, 100, 5, 0.8, 0)
    metrics.record_episode(False, 4.0, 50, 2, 0.7, 0)
    assert metrics.average_reward == pytest.approx(1.0, abs=0.01)


def test_average_steps(metrics):
    metrics.record_episode(True, 9.0, 30, 1, 0.3, 1)
    metrics.record_episode(True, 9.0, 50, 1, 0.3, 1)
    assert metrics.average_steps == pytest.approx(40.0, abs=0.1)


def test_save_and_load(tmp_path):
    path = tmp_path / "stats.json"
    m1 = TrainingMetrics(stats_file=path)
    m1.record_episode(True, 9.0, 30, 1, 0.5, 1)
    m1.save()

    assert path.exists()

    m2 = TrainingMetrics(stats_file=path)
    assert m2.total_episodes == 1
    assert m2.goal_reached_count == 1


def test_reset(tmp_path):
    path = tmp_path / "stats.json"
    m = TrainingMetrics(stats_file=path)
    m.record_episode(True, 9.0, 30, 1, 0.5, 1)
    m.save()
    m.reset()

    assert m.total_episodes == 0
    assert not path.exists()


def test_to_dict_keys(metrics):
    d = metrics.to_dict()
    for key in [
        "total_episodes",
        "recent_success_rate",
        "best_success_rate",
        "average_reward",
        "average_steps",
        "wall_hits",
        "goal_reached_count",
        "exploration_rate",
        "current_level",
        "last_updated",
    ]:
        assert key in d
