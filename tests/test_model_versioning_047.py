"""Tests de versionado de modelos para BabyIA 0.4.7."""

import pytest
from pathlib import Path


def test_model_v4_6_latest_defined_in_config():
    from config import MODEL_V4_6_LATEST

    assert MODEL_V4_6_LATEST is not None
    assert "v0_4_6" in str(
        MODEL_V4_6_LATEST
    ), f"MODEL_V4_6_LATEST no contiene v0_4_6: {MODEL_V4_6_LATEST}"


def test_model_v4_6_best_defined_in_config():
    from config import MODEL_V4_6_BEST

    assert MODEL_V4_6_BEST is not None
    assert "v0_4_6" in str(
        MODEL_V4_6_BEST
    ), f"MODEL_V4_6_BEST no contiene v0_4_6: {MODEL_V4_6_BEST}"


def test_model_v4_6_latest_is_pathlib():
    from config import MODEL_V4_6_LATEST

    assert isinstance(MODEL_V4_6_LATEST, Path)


def test_model_v4_6_best_is_pathlib():
    from config import MODEL_V4_6_BEST

    assert isinstance(MODEL_V4_6_BEST, Path)


def test_model_v4_6_in_models_dir():
    from config import MODEL_V4_6_LATEST, MODELS_DIR

    assert (
        MODEL_V4_6_LATEST.parent == MODELS_DIR
    ), f"MODEL_V4_6_LATEST no esta en MODELS_DIR: {MODEL_V4_6_LATEST.parent}"


def test_main_uses_model_v4_6():
    main_path = Path("main.py")
    if main_path.exists():
        text = main_path.read_text(encoding="utf-8")
        assert "MODEL_V4_6_LATEST" in text, "main.py no usa MODEL_V4_6_LATEST"
    else:
        pytest.skip("main.py no encontrado")


def test_old_model_v4_still_defined_for_reference():
    """MODEL_V4_LATEST/BEST deben seguir existiendo para referencia."""
    from config import MODEL_V4_BEST, MODEL_V4_LATEST

    assert MODEL_V4_LATEST is not None
    assert MODEL_V4_BEST is not None


def test_config_has_version_comment():
    """El comentario de config.py debe mencionar STATE_SIZE=40 para v0.4.6."""
    cfg_path = Path("config.py")
    if cfg_path.exists():
        text = cfg_path.read_text(encoding="utf-8")
        assert (
            "STATE_SIZE=40" in text or "STATE_SIZE = 40" in text or "0.4.6" in text
        ), "config.py no documenta la arquitectura actual (STATE_SIZE=40 o 0.4.6)"
    else:
        pytest.skip("config.py no encontrado")
