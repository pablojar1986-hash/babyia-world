import random
from collections import deque
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

STATE_SIZE = 18  # 0.2: +8 features (has_key, energy, dist_llave, dist_puerta, door_open, peligro)
ACTION_SIZE = 5
REPLAY_CAPACITY = 10_000
BATCH_SIZE = 64
GAMMA = 0.99
LR = 1e-3
EPSILON_START = 1.0
EPSILON_MIN = 0.05
EPSILON_DECAY = 0.995
TARGET_UPDATE_FREQ = 100  # pasos de entrenamiento


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
    Aprende desde cero únicamente por experiencia propia.
    No usa APIs externas ni modelos preentrenados.
    """

    def __init__(self):
        self.q_net = _QNetwork(STATE_SIZE, ACTION_SIZE)
        self.target_net = _QNetwork(STATE_SIZE, ACTION_SIZE)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.q_net.parameters(), lr=LR)
        self.buffer = deque(maxlen=REPLAY_CAPACITY)

        self.epsilon = EPSILON_START
        self.train_steps = 0
        self.last_loss = 0.0

    # ── Selección de acción ───────────────────────────────────────────────

    def select_action(self, state: np.ndarray, extra_exploration: float = 0.0) -> int:
        effective_eps = min(1.0, self.epsilon + extra_exploration)
        if random.random() < effective_eps:
            return random.randrange(ACTION_SIZE)
        with torch.no_grad():
            t = torch.FloatTensor(state).unsqueeze(0)
            return int(self.q_net(t).argmax().item())

    # ── Memoria de experiencias (replay buffer) ───────────────────────────

    def remember(self, state, action, reward, next_state, done):
        self.buffer.append((state, int(action), float(reward), next_state, bool(done)))

    # ── Entrenamiento ─────────────────────────────────────────────────────

    def train(self):
        if len(self.buffer) < BATCH_SIZE:
            return

        batch = random.sample(self.buffer, BATCH_SIZE)
        states, actions, rewards, next_states, dones = zip(*batch)

        s = torch.FloatTensor(np.array(states))
        a = torch.LongTensor(actions)
        r = torch.FloatTensor(rewards)
        ns = torch.FloatTensor(np.array(next_states))
        d = torch.FloatTensor(dones)

        current_q = self.q_net(s).gather(1, a.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            next_q = self.target_net(ns).max(1)[0]
            target_q = r + GAMMA * next_q * (1.0 - d)

        loss = nn.SmoothL1Loss()(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.q_net.parameters(), 1.0)
        self.optimizer.step()

        self.last_loss = loss.item()
        self.train_steps += 1
        self.epsilon = max(EPSILON_MIN, self.epsilon * EPSILON_DECAY)

        if self.train_steps % TARGET_UPDATE_FREQ == 0:
            self.target_net.load_state_dict(self.q_net.state_dict())

    # ── Persistencia ──────────────────────────────────────────────────────

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
