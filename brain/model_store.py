"""Versionado y persistencia de pesos del cerebro."""
import shutil
import sys
from pathlib import Path

from config import CHECKPOINT_EVERY, CHECKPOINTS_DIR, MODEL_BEST, MODEL_LATEST


class ModelStore:
    """
    Gestiona tres capas de persistencia:
      - babyia_latest.pt  -> modelo mas reciente siempre actualizado
      - babyia_best.pt    -> solo se sobreescribe si mejora la tasa de exito
      - checkpoints/      -> copias numeradas cada N episodios

    Acepta rutas opcionales para facilitar tests sin tocar el sistema de archivos real.
    """

    def __init__(self, brain,
                 model_latest: Path | None = None,
                 model_best:   Path | None = None,
                 checkpoints_dir: Path | None = None):
        self.brain            = brain
        self._latest          = Path(model_latest)    if model_latest    else MODEL_LATEST
        self._best            = Path(model_best)      if model_best      else MODEL_BEST
        self._checkpoints_dir = Path(checkpoints_dir) if checkpoints_dir else CHECKPOINTS_DIR
        self._best_rate       = 0.0
        self.last_load_error  = ""   # 0.2.2: razon del ultimo fallo de carga

    # ── Guardado ──────────────────────────────────────────────────────────────

    def save_latest(self):
        self._latest.parent.mkdir(parents=True, exist_ok=True)
        self.brain.save(str(self._latest))

    def save_best(self, success_rate: float) -> bool:
        """Guarda como mejor modelo solo si supera el record. Devuelve True si actualizo."""
        if success_rate > self._best_rate:
            self._best_rate = success_rate
            self._best.parent.mkdir(parents=True, exist_ok=True)
            self.brain.save(str(self._best))
            return True
        return False

    def save_checkpoint(self, episode: int):
        if episode % CHECKPOINT_EVERY == 0 and episode > 0:
            self._checkpoints_dir.mkdir(parents=True, exist_ok=True)
            path = self._checkpoints_dir / f"episode_{episode:04d}.pt"
            self.brain.save(str(path))

    # ── Carga ─────────────────────────────────────────────────────────────────

    def load(self) -> bool:
        """
        Carga babyia_latest.pt si existe. Devuelve True si cargo correctamente.
        Si el modelo no existe o es incompatible, devuelve False y registra la razon
        en self.last_load_error (y la imprime en stderr).
        """
        self.last_load_error = ""

        if not self._latest.exists():
            return False

        try:
            self.brain.load(str(self._latest))
            return True
        except Exception as e:
            msg = str(e)
            if "size mismatch" in msg.lower() or "mismatch" in msg.lower():
                self.last_load_error = f"Modelo incompatible (STATE_SIZE diferente): {msg[:120]}"
            else:
                self.last_load_error = f"Error al cargar modelo: {msg[:120]}"
            print(f"[model_store] {self.last_load_error}", file=sys.stderr)
            return False

    def init_best_rate(self, rate: float):
        """Inicializa el mejor record conocido (cargado desde metricas)."""
        self._best_rate = rate

    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset(self):
        for p in [self._latest, self._best]:
            if p.exists():
                p.unlink()
        if self._checkpoints_dir.exists():
            shutil.rmtree(self._checkpoints_dir)
        self._best_rate = 0.0
