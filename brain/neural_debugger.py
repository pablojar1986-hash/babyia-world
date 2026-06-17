"""
Inspeccion diagnostica del cerebro DQN sin modificar entrenamiento.
Funciones de solo lectura: no escriben pesos, epsilon ni el buffer.
No usar librerias externas adicionales.
"""

import numpy as np
import torch

_ACTION_NAMES = ["arriba", "abajo", "izquierda", "derecha", "esperar"]
_ACTION_SYMBOLS = {
    "arriba": "^",
    "abajo": "v",
    "izquierda": "<",
    "derecha": ">",
    "esperar": ".",
}


def get_q_values(brain, state: np.ndarray) -> dict[str, float]:
    """Q-values de todas las acciones para el estado dado. No modifica la red."""
    with torch.no_grad():
        t = torch.FloatTensor(state).unsqueeze(0)
        qs = brain.q_net(t).squeeze(0).tolist()
    return {name: round(q, 4) for name, q in zip(_ACTION_NAMES, qs)}


def get_action_ranking(brain, state: np.ndarray) -> list[dict]:
    """Acciones ordenadas por Q-value descendente."""
    qv = get_q_values(brain, state)
    ranked = sorted(qv.items(), key=lambda kv: kv[1], reverse=True)
    return [
        {"action": a, "q_value": q, "rank": i + 1} for i, (a, q) in enumerate(ranked)
    ]


def get_layer_activation_summary(brain, state: np.ndarray) -> list[dict]:
    """
    Activacion media de cada capa mediante forward hooks.
    Los hooks se eliminan tras la pasada: no hay efectos secundarios.
    Estructura DQN: Linear(34,128)[0] ReLU[1] Linear(128,64)[2] ReLU[3] Linear(64,5)[4]
    """
    activations: dict[str, float] = {}
    hooks = []

    def _make_hook(name: str):
        def hook(module, inp, out):
            activations[name] = float(out.detach().abs().mean().item())

        return hook

    for i, layer in enumerate(brain.q_net.net):
        hooks.append(layer.register_forward_hook(_make_hook(f"l{i}")))

    with torch.no_grad():
        brain.q_net(torch.FloatTensor(state).unsqueeze(0))

    for h in hooks:
        h.remove()

    return [
        {"name": "input", "size": len(state), "activation_mean": None},
        {
            "name": "hidden_1",
            "size": 128,
            "activation_mean": round(activations.get("l1", 0.0), 4),
        },
        {
            "name": "hidden_2",
            "size": 64,
            "activation_mean": round(activations.get("l3", 0.0), 4),
        },
        {
            "name": "output",
            "size": 5,
            "activation_mean": round(activations.get("l4", 0.0), 4),
        },
    ]


def get_brain_snapshot(
    brain, state: np.ndarray, last_action: int = 0, exploration: bool = True
) -> dict:
    """
    Snapshot completo del estado del cerebro para diagnostico visual.
    No modifica pesos, epsilon ni el replay buffer.
    """
    q_dict = get_q_values(brain, state)
    layers = get_layer_activation_summary(brain, state)
    best = max(q_dict, key=q_dict.get) if q_dict else "?"
    action_name = (
        _ACTION_NAMES[last_action] if 0 <= last_action < len(_ACTION_NAMES) else "?"
    )

    return {
        "state_size": len(state),
        "action_size": len(_ACTION_NAMES),
        "epsilon": round(brain.epsilon, 4),
        "last_action": action_name,
        "last_action_idx": last_action,
        "decision_type": "exploration" if exploration else "exploitation",
        "q_values": q_dict,
        "best_action": best,
        "replay_buffer_size": len(brain.buffer),
        "train_steps": brain.train_steps,
        "last_loss": round(brain.last_loss, 6),
        "layers": layers,
    }
