"""Configuración centralizada de BabyIA World. Sin valores mágicos dispersos."""
from pathlib import Path

# ── Rutas absolutas (relativas al archivo config.py) ──────────────────────────
ROOT_DIR        = Path(__file__).parent
DATA_DIR        = ROOT_DIR / "data"
MODELS_DIR      = ROOT_DIR / "models"
CHECKPOINTS_DIR = MODELS_DIR / "checkpoints"
DOCS_DIR        = ROOT_DIR / "docs"

# Archivos de modelo versionados
MODEL_LATEST = MODELS_DIR / "babyia_latest.pt"
MODEL_BEST   = MODELS_DIR / "babyia_best.pt"

# Archivos de datos persistentes
STATS_FILE         = DATA_DIR / "training_stats.json"
MEMORIES_FILE      = DATA_DIR / "memories.json"
AUTOBIOGRAPHY_FILE = DATA_DIR / "autobiography.json"
CONCEPTS_FILE      = DATA_DIR / "concepts.json"          # 0.2
NETWORK_STATS_FILE = DATA_DIR / "network_stats.json"     # 0.2.1
LEVEL_STATS_FILE   = DATA_DIR / "level_stats.json"       # 0.2.1

# ── Frecuencias de guardado ────────────────────────────────────────────────────
SAVE_LATEST_EVERY   = 10    # episodios entre guardados de babyia_latest.pt
SAVE_METRICS_EVERY  = 10    # episodios entre guardados de training_stats.json
CHECKPOINT_EVERY    = 100   # episodios entre checkpoints numerados

# ── Modos de ejecución ─────────────────────────────────────────────────────────
MODE_TRAIN    = "train"
MODE_WATCH    = "watch"
MODE_EVALUATE = "evaluate"

DEFAULT_EPISODES = {
    MODE_TRAIN:    1000,
    MODE_WATCH:    9999,
    MODE_EVALUATE: 100,
}

# Exploración reducida en watch/evaluate (no aprende, solo actúa)
INFERENCE_EPSILON = 0.05
