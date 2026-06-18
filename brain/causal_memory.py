"""
Memoria de relaciones causa-efecto de BabyIA.
Almacena que acciones/objetos provocaron que resultados, con nivel de confianza.
La confianza aumenta con evidencia consistente; disminuye con evidencia contraria.
No es un modelo bayesiano real — es un sistema de conteo simple con clamping.
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CausalRelation:
    cause: str
    effect: str
    successes: int = 0  # veces que cause -> effect se confirmo
    failures: int = 0  # veces que cause -> effect fallo / no ocurrio
    last_episode: int = 0

    @property
    def confidence(self) -> float:
        total = self.successes + self.failures
        if total == 0:
            return 0.0
        return round(self.successes / total, 3)

    @property
    def total_observations(self) -> int:
        return self.successes + self.failures

    def to_dict(self) -> dict:
        return {
            "cause": self.cause,
            "effect": self.effect,
            "successes": self.successes,
            "failures": self.failures,
            "confidence": self.confidence,
            "last_episode": self.last_episode,
        }


class CausalMemory:
    def __init__(self, filepath: Path):
        self._path: Path = filepath
        self._relations: dict[str, CausalRelation] = {}
        self._load()

    # ── Registro de observaciones ─────────────────────────────────────────────

    def observe(self, cause: str, effect: str, success: bool, episode: int = 0):
        """Registra una observacion de cause->effect."""
        key = f"{cause}::{effect}"
        if key not in self._relations:
            self._relations[key] = CausalRelation(cause=cause, effect=effect)
        rel = self._relations[key]
        if success:
            rel.successes += 1
        else:
            rel.failures += 1
        rel.last_episode = episode

    # ── Consultas ─────────────────────────────────────────────────────────────

    def get_confidence(self, cause: str, effect: str) -> float:
        key = f"{cause}::{effect}"
        rel = self._relations.get(key)
        return rel.confidence if rel else 0.0

    def get_relation(self, cause: str, effect: str) -> CausalRelation | None:
        return self._relations.get(f"{cause}::{effect}")

    def best_effect_for(self, cause: str) -> str | None:
        """Efecto con mayor confianza para una causa dada."""
        candidates = {
            k: r
            for k, r in self._relations.items()
            if r.cause == cause and r.total_observations >= 2
        }
        if not candidates:
            return None
        return max(candidates.values(), key=lambda r: r.confidence).effect

    def all_relations(self) -> list[CausalRelation]:
        return list(self._relations.values())

    def count_learned(self, min_confidence: float = 0.6) -> int:
        return sum(
            1
            for r in self._relations.values()
            if r.confidence >= min_confidence and r.total_observations >= 3
        )

    # ── Persistencia ──────────────────────────────────────────────────────────

    def save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = [r.to_dict() for r in self._relations.values()]
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def reset(self):
        self._relations = {}
        self.save()

    def to_dict(self) -> dict:
        return {
            "total_relations": len(self._relations),
            "learned_confident": self.count_learned(),
            "relations": [r.to_dict() for r in self._relations.values()],
        }

    def _load(self):
        if not self._path.exists():
            return
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            for entry in data:
                rel = CausalRelation(
                    cause=entry["cause"],
                    effect=entry["effect"],
                    successes=entry.get("successes", 0),
                    failures=entry.get("failures", 0),
                    last_episode=entry.get("last_episode", 0),
                )
                self._relations[f"{rel.cause}::{rel.effect}"] = rel
        except (json.JSONDecodeError, KeyError):
            self._relations = {}
