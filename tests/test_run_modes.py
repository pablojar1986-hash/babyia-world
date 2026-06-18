"""Tests de argumentos y configuración de modos de ejecución."""

import random
from unittest.mock import patch


def _parse(args):
    with patch("sys.argv", ["main.py"] + args):
        from main import parse_args

        return parse_args()


def test_default_mode_is_train():
    cfg = _parse([])
    assert cfg.mode == "train"


def test_parse_watch_mode():
    cfg = _parse(["--mode", "watch"])
    assert cfg.mode == "watch"


def test_parse_evaluate_mode():
    cfg = _parse(["--mode", "evaluate"])
    assert cfg.mode == "evaluate"


def test_parse_episodes():
    cfg = _parse(["--episodes", "50"])
    assert cfg.episodes == 50


def test_default_episodes_train():
    cfg = _parse(["--mode", "train"])
    assert cfg.episodes == 1000


def test_default_episodes_evaluate():
    cfg = _parse(["--mode", "evaluate"])
    assert cfg.episodes == 100


def test_parse_seed():
    cfg = _parse(["--seed", "42"])
    assert cfg.seed == 42


def test_reset_all_sets_all_flags():
    cfg = _parse(["--reset-all"])
    assert cfg.reset_memory
    assert cfg.reset_model
    assert cfg.reset_stats


def test_reset_memory_only():
    cfg = _parse(["--reset-memory"])
    assert cfg.reset_memory
    assert not cfg.reset_model
    assert not cfg.reset_stats


def test_set_seed_reproducible():
    from main import set_seed

    set_seed(42)
    a = random.random()
    set_seed(42)
    b = random.random()
    assert a == b


def test_set_seed_different_values():
    from main import set_seed

    set_seed(1)
    a = random.random()
    set_seed(2)
    b = random.random()
    assert a != b
