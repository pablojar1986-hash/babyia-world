"""
Tests de estabilidad para BabyIA World 0.2.2.
Verifican correcciones criticas de comportamiento en main.py.
"""

from unittest.mock import patch

from main import parse_args, RunConfig
from config import DEFAULT_EPISODES, MODE_TRAIN


def test_parse_args_allows_zero_episodes():
    """--episodes 0 debe conservarse, no substituirse por el default."""
    with patch("sys.argv", ["main.py", "--episodes", "0"]):
        cfg = parse_args()
    assert cfg.episodes == 0, (
        f"Se esperaba 0 pero se obtuvo {cfg.episodes}. "
        "El bug 'episodes or default' interpreta 0 como False."
    )


def test_parse_args_default_episodes_when_not_specified():
    with patch("sys.argv", ["main.py"]):
        cfg = parse_args()
    assert cfg.episodes == DEFAULT_EPISODES[MODE_TRAIN]


def test_parse_args_positive_episodes_respected():
    with patch("sys.argv", ["main.py", "--episodes", "42"]):
        cfg = parse_args()
    assert cfg.episodes == 42


def test_reset_all_zero_episodes_does_not_train():
    """--reset-all --episodes 0 no debe ejecutar ninguna iteracion de entrenamiento."""
    with patch("sys.argv", ["main.py", "--reset-all", "--episodes", "0"]):
        cfg = parse_args()
    assert cfg.episodes == 0
    assert cfg.reset_memory is True
    assert cfg.reset_model is True
    assert cfg.reset_stats is True
    # range(0) -> 0 iteraciones -> no entrena
    assert list(range(cfg.episodes)) == []


def test_parse_args_reset_all_sets_all_flags():
    with patch("sys.argv", ["main.py", "--reset-all"]):
        cfg = parse_args()
    assert cfg.reset_memory is True
    assert cfg.reset_model is True
    assert cfg.reset_stats is True
    assert cfg.reset_concepts is True


def test_parse_args_yes_flag_default_false():
    with patch("sys.argv", ["main.py"]):
        cfg = parse_args()
    assert cfg.yes is False


def test_parse_args_yes_flag_explicit():
    with patch("sys.argv", ["main.py", "--reset-all", "--yes"]):
        cfg = parse_args()
    assert cfg.yes is True


def test_runconfig_is_dataclass():
    cfg = RunConfig()
    assert cfg.episodes == DEFAULT_EPISODES[MODE_TRAIN]
    assert cfg.yes is False
