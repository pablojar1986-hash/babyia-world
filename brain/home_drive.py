"""
Impulso de regreso a casa: registra patron de retorno de BabyIA.
No es miedo ni apego: es una regla de entrenamiento con metricas.
Persiste en data/home_stats.json.
"""

import json
from pathlib import Path

from config import DATA_DIR

HOME_STATS_FILE = DATA_DIR / "home_stats.json"

EXTRA_STEP_PENALTY = 0.01  # penalizacion extra por cada paso tras superar el umbral


class HomeDrive:
    def __init__(self, stats_file: Path | None = None):
        self._file = Path(stats_file) if stats_file else HOME_STATS_FILE
        self.total_episodes = 0
        self.episodes_at_home = 0
        self.episodes_away = 0
        self.total_returns = 0
        self._ep_steps_out = 0
        self._ep_returned = False
        self._load()

    # ── Por episodio ──────────────────────────────────────────────────────────

    def reset_episode(self):
        self._ep_steps_out = 0
        self._ep_returned = False

    def step_outside(self):
        self._ep_steps_out += 1

    def register_return(self):
        self._ep_returned = True
        self.total_returns += 1

    def end_episode(self):
        self.total_episodes += 1
        if self._ep_returned:
            self.episodes_at_home += 1
        else:
            self.episodes_away += 1
        self._ep_steps_out = 0
        self._ep_returned = False

    # ── Senales ───────────────────────────────────────────────────────────────

    def should_return(self, threshold: int = 60) -> bool:
        return self._ep_steps_out >= threshold

    def extra_step_penalty(self, threshold: int = 60) -> float:
        excess = max(0, self._ep_steps_out - threshold)
        return -(excess * EXTRA_STEP_PENALTY)

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def return_home_rate(self) -> float:
        if not self.total_episodes:
            return 0.0
        return round(self.episodes_at_home / self.total_episodes, 3)

    def to_dict(self) -> dict:
        return {
            "total_episodes": self.total_episodes,
            "episodes_at_home": self.episodes_at_home,
            "episodes_away": self.episodes_away,
            "total_returns": self.total_returns,
            "return_home_rate": self.return_home_rate,
        }

    def save(self):
        self._file.parent.mkdir(exist_ok=True)
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def reset(self):
        self.total_episodes = self.episodes_at_home = self.episodes_away = 0
        self.total_returns = self._ep_steps_out = 0
        self._ep_returned = False
        if self._file.exists():
            self._file.unlink()

    def _load(self):
        try:
            with open(self._file, encoding="utf-8") as f:
                d = json.load(f)
            self.total_episodes = d.get("total_episodes", 0)
            self.episodes_at_home = d.get("episodes_at_home", 0)
            self.episodes_away = d.get("episodes_away", 0)
            self.total_returns = d.get("total_returns", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
