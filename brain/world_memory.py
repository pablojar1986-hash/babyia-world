"""
Memoria de visitas a mundos: que mundos visito BabyIA y con que resultado.
Persiste en data/world_history.json.
"""

import json
from datetime import datetime
from pathlib import Path

from config import DATA_DIR

WORLD_HISTORY_FILE = DATA_DIR / "world_history.json"


class WorldMemory:
    def __init__(self, history_file: Path | None = None):
        self._file = Path(history_file) if history_file else WORLD_HISTORY_FILE
        self.visits: list[dict] = []
        self._load()

    def record_visit(
        self,
        episode: int,
        world_id: str,
        entered_from: str,
        reward_gained: float,
        risk_events: int,
        returned_home: bool,
        steps_spent: int,
    ):
        self.visits.append(
            {
                "episode": episode,
                "world_id": world_id,
                "entered_from": entered_from,
                "reward_gained": round(reward_gained, 3),
                "risk_events": risk_events,
                "returned_home": returned_home,
                "steps_spent": steps_spent,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_visits_for(self, world_id: str) -> list[dict]:
        return [v for v in self.visits if v["world_id"] == world_id]

    def total_visits(self, world_id: str) -> int:
        return len(self.get_visits_for(world_id))

    def average_reward(self, world_id: str) -> float:
        vs = self.get_visits_for(world_id)
        return round(sum(v["reward_gained"] for v in vs) / len(vs), 3) if vs else 0.0

    def return_home_rate(self, world_id: str) -> float:
        vs = self.get_visits_for(world_id)
        return (
            round(sum(1 for v in vs if v["returned_home"]) / len(vs), 3) if vs else 0.0
        )

    def average_risk(self, world_id: str) -> float:
        vs = self.get_visits_for(world_id)
        return round(sum(v["risk_events"] for v in vs) / len(vs), 3) if vs else 0.0

    def summary(self) -> dict:
        worlds = {v["world_id"] for v in self.visits}
        return {
            wid: {
                "visits": self.total_visits(wid),
                "average_reward": self.average_reward(wid),
                "return_home_rate": self.return_home_rate(wid),
                "average_risk": self.average_risk(wid),
            }
            for wid in worlds
        }

    def save(self):
        self._file.parent.mkdir(exist_ok=True)
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump({"visits": self.visits}, f, indent=2, ensure_ascii=False)

    def reset(self):
        self.visits = []
        if self._file.exists():
            self._file.unlink()

    def _load(self):
        try:
            with open(self._file, encoding="utf-8") as f:
                self.visits = json.load(f).get("visits", [])
        except (FileNotFoundError, json.JSONDecodeError):
            pass
