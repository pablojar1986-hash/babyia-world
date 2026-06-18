"""
brain/baby_brain.py — Cerebro DQN de BabyIA.

0.4.6:
- Double DQN: selecciona accion con q_net, evalua con target_net (reduce sobreestimacion)
- Prioritized Experience Replay: muestrea por error TD (aprende mas de sorpresas)
- STATE_SIZE 34 -> 40 (incluye 6 features de percepcion)
- REPLAY_CAPACITY 10k -> 50k, EPSILON_DECAY 0.995 -> 0.998
"""

import random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from config import ACTION_SIZE, STATE_SIZE  # fuente de verdad en config.py

REPLAY_CAPACITY = 50_000  # ampliado para grids 16x16
BATCH_SIZE = 64
GAMMA = 0.99
LR = 1e-3
EPSILON_START = 1.0
EPSILON_MIN = 0.05
EPSILON_DECAY = 0.998  # decay mas lento para grids grandes
TARGET_UPDATE_FREQ = 100

# Prioritized Experience Replay
_PER_ALPHA = 0.6  # cuanto priorizar (0=uniforme, 1=full-prio)
_PER_BETA_START = 0.4  # correccion de sesgo inicial
_PER_BETA_INCREMENT = 1e-4
_PER_EPSILON = 1e-6  # prioridad minima para evitar ceros


class _SumTree:
    """Arbol binario de suma para muestreo O(log n) por prioridad."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.tree = np.zeros(2 * capacity - 1, dtype=np.float64)
        self.data: list = [None] * capacity
        self._write = 0
        self._n_entries = 0

    def _propagate(self, idx: int, delta: float) -> None:
        while idx > 0:
            idx = (idx - 1) // 2
            self.tree[idx] += delta

    def _retrieve(self, idx: int, s: float) -> int:
        while True:
            left = 2 * idx + 1
            right = left + 1
            if left >= len(self.tree):
                return idx
            if s <= self.tree[left]:
                idx = left
            else:
                s -= self.tree[left]
                idx = right

    @property
    def total(self) -> float:
        return float(self.tree[0])

    def add(self, priority: float, data) -> None:
        idx = self._write + self.capacity - 1
        self.data[self._write] = data
        self.update(idx, priority)
        self._write = (self._write + 1) % self.capacity
        self._n_entries = min(self._n_entries + 1, self.capacity)

    def update(self, idx: int, priority: float) -> None:
        delta = priority - self.tree[idx]
        self.tree[idx] = priority
        self._propagate(idx, delta)

    def get(self, s: float):
        s = min(s, self.total - 1e-10)
        s = max(s, 0.0)
        idx = self._retrieve(0, s)
        data_idx = idx - self.capacity + 1
        return idx, float(self.tree[idx]), self.data[data_idx]

    def __len__(self) -> int:
        return self._n_entries


class _PrioritizedReplayBuffer:
    """Replay buffer con Prioritized Experience Replay (PER)."""

    def __init__(self, capacity: int):
        self._tree = _SumTree(capacity)
        self._beta = _PER_BETA_START
        self._max_priority = 1.0

    def add(self, experience) -> None:
        self._tree.add(self._max_priority, experience)

    def sample(self, batch_size: int):
        batch, indices, raw_weights = [], [], []
        segment = self._tree.total / batch_size
        self._beta = min(1.0, self._beta + _PER_BETA_INCREMENT)
        n = len(self._tree)

        for i in range(batch_size):
            s = random.uniform(segment * i, segment * (i + 1))
            idx, priority, data = self._tree.get(s)
            prob = priority / (self._tree.total + 1e-10)
            prob = max(prob, _PER_EPSILON)
            raw_weights.append((prob * n) ** (-self._beta))
            indices.append(idx)
            batch.append(data)

        max_w = max(raw_weights)
        weights = np.array([w / max_w for w in raw_weights], dtype=np.float32)
        return batch, indices, weights

    def update_priorities(self, indices, td_errors) -> None:
        for idx, error in zip(indices, td_errors):
            priority = (float(abs(error)) + _PER_EPSILON) ** _PER_ALPHA
            self._tree.update(idx, priority)
            self._max_priority = max(self._max_priority, priority)

    def __len__(self) -> int:
        return len(self._tree)


class _QNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_size),
        )

    def forward(self, x):
        return self.net(x)


class BabyBrain:
    """
    Cerebro de BabyIA basado en Deep Q-Network (DQN).
    0.4.6: Double DQN + Prioritized Experience Replay.
    Aprende desde cero unicamente por experiencia propia.
    No usa APIs externas ni modelos preentrenados.
    """

    def __init__(self):
        self.q_net = _QNetwork(STATE_SIZE, ACTION_SIZE)
        self.target_net = _QNetwork(STATE_SIZE, ACTION_SIZE)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.q_net.parameters(), lr=LR)
        self.buffer = _PrioritizedReplayBuffer(REPLAY_CAPACITY)

        self.epsilon = EPSILON_START
        self.train_steps = 0
        self.last_loss = 0.0
        self.last_decision: dict = {
            "action": 0,
            "decision_type": "unknown",
            "effective_epsilon": 0.0,
            "q_values": [],
        }

    # ── Seleccion de accion ───────────────────────────────────────────────────

    def select_action(self, state: np.ndarray, extra_exploration: float = 0.0) -> int:
        effective_eps = min(1.0, self.epsilon + extra_exploration)
        if random.random() < effective_eps:
            action = random.randrange(ACTION_SIZE)
            self.last_decision = {
                "action": action,
                "decision_type": "exploration",
                "effective_epsilon": round(effective_eps, 4),
                "q_values": [],
            }
            return action
        with torch.no_grad():
            t = torch.FloatTensor(state).unsqueeze(0)
            qs = self.q_net(t).squeeze(0)
            action = int(qs.argmax().item())
        self.last_decision = {
            "action": action,
            "decision_type": "exploitation",
            "effective_epsilon": round(effective_eps, 4),
            "q_values": qs.tolist(),
        }
        return action

    # ── Memoria de experiencias ───────────────────────────────────────────────

    def remember(self, state, action, reward, next_state, done):
        self.buffer.add((state, int(action), float(reward), next_state, bool(done)))

    # ── Entrenamiento ─────────────────────────────────────────────────────────

    def train(self):
        if len(self.buffer) < BATCH_SIZE:
            return

        batch, indices, weights = self.buffer.sample(BATCH_SIZE)
        states, actions, rewards, next_states, dones = zip(*batch)

        s = torch.FloatTensor(np.array(states))
        a = torch.LongTensor(actions)
        r = torch.FloatTensor(rewards)
        ns = torch.FloatTensor(np.array(next_states))
        d = torch.FloatTensor(dones)
        w = torch.FloatTensor(weights)

        current_q = self.q_net(s).gather(1, a.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            # Double DQN: q_net selecciona accion, target_net evalua valor
            next_actions = self.q_net(ns).argmax(1, keepdim=True)
            next_q = self.target_net(ns).gather(1, next_actions).squeeze(1)
            target_q = r + GAMMA * next_q * (1.0 - d)

        td_errors = (current_q.detach() - target_q).abs().cpu().numpy()
        self.buffer.update_priorities(indices, td_errors)

        loss = (w * nn.SmoothL1Loss(reduction="none")(current_q, target_q)).mean()
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.q_net.parameters(), 1.0)
        self.optimizer.step()

        self.last_loss = loss.item()
        self.train_steps += 1
        self.epsilon = max(EPSILON_MIN, self.epsilon * EPSILON_DECAY)

        if self.train_steps % TARGET_UPDATE_FREQ == 0:
            self.target_net.load_state_dict(self.q_net.state_dict())

    # ── Persistencia ──────────────────────────────────────────────────────────

    def save(self, path="models/baby_brain.pt"):
        Path(path).parent.mkdir(exist_ok=True)
        torch.save(
            {
                "q_net": self.q_net.state_dict(),
                "epsilon": self.epsilon,
                "train_steps": self.train_steps,
            },
            path,
        )

    def load(self, path="models/baby_brain.pt"):
        data = torch.load(path, map_location="cpu", weights_only=False)
        self.q_net.load_state_dict(data["q_net"])
        self.target_net.load_state_dict(data["q_net"])
        self.epsilon = data.get("epsilon", EPSILON_MIN)
        self.train_steps = data.get("train_steps", 0)
