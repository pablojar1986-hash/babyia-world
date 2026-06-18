"""
Calculo de preferencia simulada de BabyIA por mundos.
Formula: preferencia = recompensa_media + retorno*5 - riesgo*4 - pasos*0.05
Estas son metricas estadisticas, no emociones ni preferencias reales.
"""

import json
from pathlib import Path

from config import DATA_DIR

PREFERENCES_FILE = DATA_DIR / "world_preferences.json"

RETURN_WEIGHT = 5.0
RISK_WEIGHT = 4.0
STEPS_FACTOR = 0.05


class PreferenceTracker:
    def __init__(self, prefs_file: Path | None = None):
        self._file = Path(prefs_file) if prefs_file else PREFERENCES_FILE
        self._raw: dict[str, dict] = {}

    def update(
        self,
        world_id: str,
        reward: float,
        risk_events: int,
        returned_home: bool,
        steps: int,
    ):
        if world_id not in self._raw:
            self._raw[world_id] = {
                "visits": 0,
                "total_reward": 0.0,
                "total_risk": 0,
                "total_returned": 0,
                "total_steps": 0,
            }
        d = self._raw[world_id]
        d["visits"] += 1
        d["total_reward"] += reward
        d["total_risk"] += risk_events
        d["total_returned"] += int(returned_home)
        d["total_steps"] += steps

    def get_score(self, world_id: str) -> float:
        d = self._raw.get(world_id)
        if not d or d["visits"] == 0:
            return 0.0
        v = d["visits"]
        avg_r = d["total_reward"] / v
        avg_ri = d["total_risk"] / v
        ret_r = d["total_returned"] / v
        avg_s = d["total_steps"] / v
        return (
            avg_r + ret_r * RETURN_WEIGHT - avg_ri * RISK_WEIGHT - avg_s * STEPS_FACTOR
        )

    def get_all_scores(self) -> dict[str, float]:
        return {wid: self.get_score(wid) for wid in self._raw}

    def best_world(self) -> str | None:
        scores = self.get_all_scores()
        return max(scores, key=scores.__getitem__) if scores else None

    def to_dict(self) -> dict:
        result = {}
        for wid, d in self._raw.items():
            v = d["visits"]
            if not v:
                continue
            result[wid] = {
                "visits": v,
                "average_reward": round(d["total_reward"] / v, 3),
                "average_risk": round(d["total_risk"] / v, 3),
                "return_home_rate": round(d["total_returned"] / v, 3),
                "preference_score": round(self.get_score(wid), 3),
            }
        return result

    def save(self):
        self._file.parent.mkdir(exist_ok=True)
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def reset(self):
        self._raw = {}
        if self._file.exists():
            self._file.unlink()
