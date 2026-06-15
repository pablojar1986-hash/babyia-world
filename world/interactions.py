"""
Reglas de interaccion causa-efecto de BabyIA World 0.2.

Cada funcion devuelve un dict estandar:
  {
    "success"       : bool,
    "message"       : str,
    "reward_delta"  : float,
    "concept_signal": dict,
  }

El Trainer aplica los efectos sobre Inventory y ConceptMemory.
Este modulo solo describe que pasa; no modifica estado directamente.
"""

from __future__ import annotations


def interact_key(has_key: bool, first_time: bool) -> dict:
    """BabyIA intenta recoger una llave."""
    if has_key:
        return {
            "success": False,
            "message": "Ya tengo una llave.",
            "reward_delta": 0.0,
            "concept_signal": {},
        }
    bonus = 3.0 if first_time else 0.5
    return {
        "success": True,
        "message": "Recogi una llave.",
        "reward_delta": bonus,
        "concept_signal": {"key_found": True},
    }


def interact_door_closed(has_key: bool) -> dict:
    """BabyIA intenta entrar en una puerta cerrada."""
    if not has_key:
        return {
            "success": False,
            "message": "La puerta no se abrio. Necesito algo para abrirla.",
            "reward_delta": -0.5,
            "concept_signal": {"door_requires": "unknown_tool"},
        }
    return {
        "success": True,
        "message": "La llave abrio la puerta.",
        "reward_delta": 5.0,
        "concept_signal": {"key_opens": "door"},
    }


def interact_food(energy: float) -> dict:
    """BabyIA consume comida."""
    bonus = 2.0 if energy < 0.5 else 0.5
    return {
        "success": True,
        "message": "Comi y recupere energia.",
        "reward_delta": bonus,
        "concept_signal": {"food_restores": "energy"},
    }


def interact_danger() -> dict:
    """BabyIA entra en zona peligrosa."""
    return {
        "success": False,
        "message": "Esta zona es peligrosa. Perdi energia.",
        "reward_delta": -2.0,
        "concept_signal": {"danger_reduces": "energy"},
    }


def interact_unknown(first_time: bool) -> dict:
    """BabyIA toca un objeto desconocido."""
    return {
        "success": True,
        "message": "Encontre un objeto desconocido.",
        "reward_delta": 1.0 if first_time else 0.0,
        "concept_signal": {"unknown_object": "discovered"},
    }
