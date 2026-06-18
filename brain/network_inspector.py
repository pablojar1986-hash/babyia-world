"""Inspeccion de arquitectura de la red neuronal DQN de BabyIA."""

import json
from datetime import datetime
from pathlib import Path

from config import DATA_DIR

NETWORK_STATS_FILE = DATA_DIR / "network_stats.json"


def inspect_network(model) -> dict:
    """Extrae input_size, output_size, conteo de parametros y capas lineales."""
    layers = []
    total_params = 0
    for _name, module in model.named_modules():
        if type(module).__name__ == "Linear":
            p = module.in_features * module.out_features + module.out_features
            layers.append(
                {
                    "name": _name,
                    "in": module.in_features,
                    "out": module.out_features,
                    "params": p,
                }
            )
            total_params += p

    return {
        "input_size": layers[0]["in"] if layers else 0,
        "output_size": layers[-1]["out"] if layers else 0,
        "total_params": total_params,
        "layer_sizes": [layer["in"] for layer in layers]
        + ([layers[-1]["out"]] if layers else []),
        "layers": layers,
    }


def is_compatible(model, expected_input_size: int) -> bool:
    """Devuelve True si el modelo tiene el tamano de entrada esperado."""
    return inspect_network(model)["input_size"] == expected_input_size


def save_network_stats(model, stats_file: Path | None = None) -> dict:
    """Guarda metadatos de arquitectura en data/network_stats.json."""
    path = Path(stats_file) if stats_file else NETWORK_STATS_FILE
    path.parent.mkdir(exist_ok=True)
    info = inspect_network(model)
    info["last_updated"] = datetime.now().isoformat()
    info["version"] = "0.4.6"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    return info


def load_network_stats(stats_file: Path | None = None) -> dict:
    """Carga metadatos guardados previamente. Devuelve {} si no existe."""
    path = Path(stats_file) if stats_file else NETWORK_STATS_FILE
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
