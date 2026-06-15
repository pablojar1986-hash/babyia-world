"""Metricas de entrenamiento persistentes en data/training_stats.json."""
import json
from collections import deque
from datetime import datetime
from pathlib import Path

from config import STATS_FILE

WINDOW = 20  # episodios recientes para calcular tasas


class TrainingMetrics:
    """
    Registra estadisticas de entrenamiento y las persiste en JSON.
    Acepta stats_file opcional para facilitar tests.
    """

    def __init__(self, stats_file: Path | None = None):
        self._file = Path(stats_file) if stats_file else STATS_FILE
        self._init_state()
        self._load()

    # ── Estado interno ────────────────────────────────────────────────────────

    def _init_state(self):
        self.total_episodes      = 0
        self.goal_reached_count  = 0
        self.total_wall_hits     = 0
        self.best_success_rate   = 0.0
        self.exploration_rate    = 1.0
        self.current_level       = 0
        # 0.2 — contadores de objetos
        self.keys_collected      = 0
        self.doors_opened        = 0
        self.food_consumed       = 0
        self.danger_entries      = 0
        self.concepts_discovered = 0
        self.interactions_ok     = 0
        self.interactions_fail   = 0
        # 0.2.1 — metricas por nivel
        self.level_stats: dict[str, dict] = {}
        self._successes = deque(maxlen=WINDOW)
        self._rewards   = deque(maxlen=WINDOW)
        self._steps     = deque(maxlen=WINDOW)

    # ── Registro ──────────────────────────────────────────────────────────────

    def record_episode(self, reached_goal: bool, reward: float,
                       steps: int, wall_hits: int,
                       epsilon: float, level: int,
                       # 0.2 opcionales (compatibilidad hacia atras)
                       keys: int = 0, doors: int = 0, food: int = 0,
                       danger: int = 0, concepts: int = 0,
                       ok: int = 0, fail: int = 0):
        self.total_episodes += 1
        if reached_goal:
            self.goal_reached_count += 1
        self.total_wall_hits  += wall_hits
        self.exploration_rate  = epsilon
        self.current_level     = level
        # 0.2
        self.keys_collected      += keys
        self.doors_opened        += doors
        self.food_consumed       += food
        self.danger_entries      += danger
        self.concepts_discovered  = concepts  # total acumulado (no delta)
        self.interactions_ok     += ok
        self.interactions_fail   += fail

        self._successes.append(1 if reached_goal else 0)
        self._rewards.append(reward)
        self._steps.append(steps)

        # 0.2.1 — acumulado por nivel
        lk = str(level)
        if lk not in self.level_stats:
            self.level_stats[lk] = {"episodes": 0, "successes": 0, "total_reward": 0.0}
        self.level_stats[lk]["episodes"] += 1
        if reached_goal:
            self.level_stats[lk]["successes"] += 1
        self.level_stats[lk]["total_reward"] += reward

        rate = self.recent_success_rate
        if rate > self.best_success_rate:
            self.best_success_rate = rate

    # ── Propiedades calculadas ─────────────────────────────────────────────────

    @property
    def recent_success_rate(self) -> float:
        if not self._successes:
            return 0.0
        return round(sum(self._successes) / len(self._successes), 3)

    @property
    def average_reward(self) -> float:
        if not self._rewards:
            return 0.0
        return round(sum(self._rewards) / len(self._rewards), 2)

    @property
    def average_steps(self) -> float:
        if not self._steps:
            return 0.0
        return round(sum(self._steps) / len(self._steps), 1)

    # ── Serializacion ──────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "total_episodes"      : self.total_episodes,
            "recent_success_rate" : self.recent_success_rate,
            "best_success_rate"   : round(self.best_success_rate, 3),
            "average_reward"      : self.average_reward,
            "average_steps"       : self.average_steps,
            "wall_hits"           : self.total_wall_hits,
            "goal_reached_count"  : self.goal_reached_count,
            "exploration_rate"    : round(self.exploration_rate, 3),
            "current_level"       : self.current_level,
            # 0.2
            "keys_collected"      : self.keys_collected,
            "doors_opened"        : self.doors_opened,
            "food_consumed"       : self.food_consumed,
            "danger_entries"      : self.danger_entries,
            "concepts_discovered" : self.concepts_discovered,
            "interactions_ok"     : self.interactions_ok,
            "interactions_fail"   : self.interactions_fail,
            "level_stats"         : self.level_stats,
            "last_updated"        : datetime.now().isoformat(),
        }

    def save(self):
        self._file.parent.mkdir(exist_ok=True)
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def reset(self):
        if self._file.exists():
            self._file.unlink()
        self._init_state()

    def _load(self):
        try:
            with open(self._file, encoding="utf-8") as f:
                d = json.load(f)
            self.total_episodes     = d.get("total_episodes", 0)
            self.goal_reached_count = d.get("goal_reached_count", 0)
            self.total_wall_hits    = d.get("wall_hits", 0)
            self.best_success_rate  = d.get("best_success_rate", 0.0)
            self.exploration_rate   = d.get("exploration_rate", 1.0)
            self.current_level      = d.get("current_level", 0)
            # 0.2
            self.keys_collected      = d.get("keys_collected", 0)
            self.doors_opened        = d.get("doors_opened", 0)
            self.food_consumed       = d.get("food_consumed", 0)
            self.danger_entries      = d.get("danger_entries", 0)
            self.concepts_discovered = d.get("concepts_discovered", 0)
            self.interactions_ok     = d.get("interactions_ok", 0)
            self.interactions_fail   = d.get("interactions_fail", 0)
            self.level_stats         = d.get("level_stats", {})
        except (FileNotFoundError, json.JSONDecodeError):
            pass
