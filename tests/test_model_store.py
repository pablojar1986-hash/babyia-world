import pytest
from brain.baby_brain import BabyBrain
from brain.model_store import ModelStore


@pytest.fixture
def store(tmp_path):
    brain = BabyBrain()
    return ModelStore(
        brain,
        model_latest=tmp_path / "latest.pt",
        model_best=tmp_path / "best.pt",
        checkpoints_dir=tmp_path / "checkpoints",
    )


def test_save_latest(store, tmp_path):
    store.save_latest()
    assert (tmp_path / "latest.pt").exists()


def test_load_returns_false_when_no_model(store):
    assert store.load() is False


def test_load_returns_true_after_save(store, tmp_path):
    store.save_latest()
    brain2 = BabyBrain()
    store2 = ModelStore(brain2, model_latest=tmp_path / "latest.pt",
                        model_best=tmp_path / "best.pt",
                        checkpoints_dir=tmp_path / "checkpoints")
    assert store2.load() is True


def test_save_best_only_if_improves(store, tmp_path):
    # Primera vez: siempre guarda
    improved = store.save_best(0.5)
    assert improved is True
    assert (tmp_path / "best.pt").exists()

    # Mismo valor: no guarda
    improved2 = store.save_best(0.5)
    assert improved2 is False

    # Mejor valor: guarda
    improved3 = store.save_best(0.8)
    assert improved3 is True


def test_save_checkpoint_at_interval(store, tmp_path):
    store.save_checkpoint(100)
    assert (tmp_path / "checkpoints" / "episode_0100.pt").exists()


def test_no_checkpoint_before_interval(store, tmp_path):
    store.save_checkpoint(50)
    assert not (tmp_path / "checkpoints").exists() or \
           len(list((tmp_path / "checkpoints").iterdir())) == 0


def test_reset_removes_files(store, tmp_path):
    store.save_latest()
    store.save_best(0.9)
    store.save_checkpoint(100)
    store.reset()

    assert not (tmp_path / "latest.pt").exists()
    assert not (tmp_path / "best.pt").exists()


def test_init_best_rate(store):
    store.init_best_rate(0.75)
    # Con un valor menor no debe guardar
    improved = store.save_best(0.5)
    assert improved is False


# 0.2.2 ── reporte de errores ────────────────────────────────────────────────

def test_last_load_error_empty_initially(store):
    assert store.last_load_error == ""


def test_load_no_error_when_no_file(store):
    result = store.load()
    assert result is False
    assert store.last_load_error == ""   # no hay archivo -> no es un error


def test_model_load_reports_incompatible_model(tmp_path):
    """Modelo guardado con input_size diferente debe dar False y registrar razon."""
    import torch
    import torch.nn as nn
    from brain.baby_brain import BabyBrain

    # Guardar modelo con tamano de entrada incorrecto (10 en vez de 18)
    wrong_net = nn.Sequential(
        nn.Linear(10, 128), nn.ReLU(),
        nn.Linear(128, 64), nn.ReLU(),
        nn.Linear(64, 5),
    )
    model_file = tmp_path / "bad_brain.pt"
    torch.save({"q_net": wrong_net.state_dict(), "epsilon": 0.5, "train_steps": 0},
               model_file)

    brain = BabyBrain()
    store = ModelStore(brain, model_latest=model_file,
                       model_best=tmp_path / "best.pt",
                       checkpoints_dir=tmp_path / "ckpt")
    result = store.load()

    assert result is False
    assert store.last_load_error != "", "Debe registrar razon del fallo"
