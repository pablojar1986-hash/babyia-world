"""
Memoria conceptual de BabyIA — relaciones causa-efecto aprendidas por experiencia.

Los conceptos son relaciones estadisticas, NO conocimiento real ni conciencia.
Se guardan en data/concepts.json y se actualizan cada episodio.
"""

import json
from pathlib import Path

from config import CONCEPTS_FILE

# Cuantas veces debe confirmarse una relacion antes de considerarla "aprendida"
CONFIDENCE_THRESHOLD = 0.7
CONFIDENCE_GAIN_OK = 0.15  # confirmacion exitosa
CONFIDENCE_GAIN_NEW = 0.05  # primera observacion
CONFIDENCE_LOSS = 0.10  # hipotesis fallida


class ConceptMemory:
    """
    Gestiona conceptos descubiertos por BabyIA mediante experiencia.
    Acepta concepts_file opcional para tests.
    """

    def __init__(self, concepts_file: Path | None = None):
        self._file = Path(concepts_file) if concepts_file else CONCEPTS_FILE
        self.concepts: dict[str, dict] = {}  # name → concept
        self._load()

    # ── Actualizacion ─────────────────────────────────────────────────────────

    def observe(self, concept_signal: dict, success: bool, episode: int):
        """
        Registra una observacion de la relacion descrita en concept_signal.
        success=True sube confianza; False la baja.
        """
        for relation, value in concept_signal.items():
            key = f"{relation}:{value}"
            if key not in self.concepts:
                self._create(key, relation, str(value), episode)
                gain = CONFIDENCE_GAIN_NEW
            else:
                gain = CONFIDENCE_GAIN_OK if success else -CONFIDENCE_LOSS

            c = self.concepts[key]
            c["confidence"] = round(min(1.0, max(0.0, c["confidence"] + gain)), 3)
            c["evidence_count"] += 1 if success else 0
            c["last_seen_episode"] = episode

    def top_concepts(self, n: int = 3) -> list[dict]:
        """Devuelve los n conceptos con mayor confianza."""
        ranked = sorted(
            self.concepts.values(), key=lambda c: c["confidence"], reverse=True
        )
        return ranked[:n]

    def is_learned(self, key: str) -> bool:
        """True si la confianza del concepto supera el umbral."""
        return self.concepts.get(key, {}).get("confidence", 0.0) >= CONFIDENCE_THRESHOLD

    def total(self) -> int:
        return len(self.concepts)

    def reset(self):
        self.concepts = {}
        if self._file.exists():
            self._file.unlink()

    # ── Persistencia ──────────────────────────────────────────────────────────

    def save(self):
        self._file.parent.mkdir(exist_ok=True)
        data = {"concepts": list(self.concepts.values())}
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load(self):
        try:
            with open(self._file, encoding="utf-8") as f:
                data = json.load(f)
            for c in data.get("concepts", []):
                key = f"{c['relation']}:{c['value']}"
                self.concepts[key] = c
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _create(self, key: str, relation: str, value: str, episode: int):
        self.concepts[key] = {
            "name": key,
            "relation": relation,
            "value": value,
            "confidence": CONFIDENCE_GAIN_NEW,
            "evidence_count": 0,
            "first_discovered_episode": episode,
            "last_seen_episode": episode,
        }
