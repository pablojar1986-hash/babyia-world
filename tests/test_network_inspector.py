"""Tests para brain/network_inspector.py."""

import torch.nn as nn

from brain.network_inspector import (
    inspect_network,
    is_compatible,
    save_network_stats,
    load_network_stats,
)


def _make_model():
    return nn.Sequential(
        nn.Linear(18, 128),
        nn.ReLU(),
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Linear(64, 5),
    )


def test_inspect_returns_dict():
    assert isinstance(inspect_network(_make_model()), dict)


def test_inspect_input_size():
    assert inspect_network(_make_model())["input_size"] == 18


def test_inspect_output_size():
    assert inspect_network(_make_model())["output_size"] == 5


def test_inspect_param_count():
    # 18*128+128 + 128*64+64 + 64*5+5
    expected = (18 * 128 + 128) + (128 * 64 + 64) + (64 * 5 + 5)
    assert inspect_network(_make_model())["total_params"] == expected


def test_inspect_layers_count():
    assert len(inspect_network(_make_model())["layers"]) == 3


def test_inspect_layer_sizes():
    info = inspect_network(_make_model())
    assert info["layer_sizes"][0] == 18
    assert info["layer_sizes"][-1] == 5


def test_is_compatible_true():
    assert is_compatible(_make_model(), 18) is True


def test_is_compatible_false():
    assert is_compatible(_make_model(), 10) is False


def test_save_creates_file(tmp_path):
    p = tmp_path / "net_stats.json"
    save_network_stats(_make_model(), stats_file=p)
    assert p.exists()


def test_save_returns_dict(tmp_path):
    p = tmp_path / "net_stats.json"
    info = save_network_stats(_make_model(), stats_file=p)
    assert isinstance(info, dict)
    assert info["input_size"] == 18


def test_save_includes_version(tmp_path):
    p = tmp_path / "net_stats.json"
    info = save_network_stats(_make_model(), stats_file=p)
    assert info["version"] == "0.4.6"


def test_load_after_save(tmp_path):
    p = tmp_path / "net_stats.json"
    save_network_stats(_make_model(), stats_file=p)
    loaded = load_network_stats(stats_file=p)
    assert loaded["input_size"] == 18
    assert loaded["output_size"] == 5
    assert loaded["version"] == "0.4.6"


def test_load_missing_returns_empty(tmp_path):
    result = load_network_stats(stats_file=tmp_path / "nonexistent.json")
    assert result == {}


# 0.2.2 ── test requerido por spec ───────────────────────────────────────────


def test_network_stats_file_created(tmp_path):
    """save_network_stats crea el archivo y usa version 0.4.6."""
    p = tmp_path / "net.json"
    save_network_stats(_make_model(), stats_file=p)
    assert p.exists()
    loaded = load_network_stats(stats_file=p)
    assert loaded["version"] == "0.4.6"
    assert loaded["input_size"] == 18
