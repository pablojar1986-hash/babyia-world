"""Tests de HomeDrive: impulso de regreso a casa."""
import pytest
from pathlib import Path

from brain.home_drive import HomeDrive


def make_hd(tmp: Path | None = None) -> HomeDrive:
    return HomeDrive(stats_file=tmp)


def test_initial_state(tmp_path):
    hd = make_hd(tmp_path / "home_stats.json")
    assert hd.total_episodes   == 0
    assert hd.episodes_at_home == 0
    assert hd.episodes_away    == 0
    assert hd.return_home_rate == 0.0


def test_step_outside_increments():
    hd = make_hd()
    hd.step_outside()
    hd.step_outside()
    assert hd._ep_steps_out == 2


def test_should_return_false_below_threshold():
    hd = make_hd()
    for _ in range(59):
        hd.step_outside()
    assert not hd.should_return(threshold=60)


def test_should_return_true_at_threshold():
    hd = make_hd()
    for _ in range(60):
        hd.step_outside()
    assert hd.should_return(threshold=60)


def test_register_return(tmp_path):
    hd = make_hd(tmp_path / "s.json")
    hd.register_return()
    assert hd._ep_returned is True
    assert hd.total_returns == 1


def test_end_episode_at_home(tmp_path):
    hd = make_hd(tmp_path / "s.json")
    hd.register_return()
    hd.end_episode()
    assert hd.total_episodes   == 1
    assert hd.episodes_at_home == 1
    assert hd.episodes_away    == 0


def test_end_episode_away(tmp_path):
    hd = make_hd(tmp_path / "s.json")
    hd.end_episode()   # sin registrar retorno
    assert hd.episodes_away    == 1
    assert hd.episodes_at_home == 0


def test_return_home_rate(tmp_path):
    hd = make_hd(tmp_path / "s.json")
    hd.register_return(); hd.end_episode()
    hd.end_episode()
    assert hd.return_home_rate == 0.5


def test_reset_episode_clears_ep_state():
    hd = make_hd()
    hd.step_outside(); hd.step_outside()
    hd.register_return()
    hd.reset_episode()
    assert hd._ep_steps_out == 0
    assert hd._ep_returned  is False


def test_save_and_load(tmp_path):
    f = tmp_path / "home_stats.json"
    hd = HomeDrive(stats_file=f)
    hd.register_return(); hd.end_episode()
    hd.save()
    assert f.exists()
    hd2 = HomeDrive(stats_file=f)
    assert hd2.total_episodes   == 1
    assert hd2.episodes_at_home == 1
    assert hd2.total_returns    == 1
