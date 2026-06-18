"""Tests de Double DQN — BabyIA 0.4.6."""

import inspect

import numpy as np
import torch

from brain.baby_brain import EPSILON_DECAY, REPLAY_CAPACITY, STATE_SIZE, BabyBrain


class TestDoubleDQNImplementation:
    def test_train_uses_argmax_from_q_net(self):
        src = inspect.getsource(BabyBrain.train)
        assert "q_net(ns).argmax" in src

    def test_train_uses_target_net_gather(self):
        src = inspect.getsource(BabyBrain.train)
        assert "target_net(ns).gather" in src

    def test_train_does_not_use_target_net_max(self):
        """Vanilla DQN usa target_net(ns).max(1)[0]; Double DQN no debe usarlo."""
        src = inspect.getsource(BabyBrain.train)
        assert "target_net(ns).max(1)" not in src

    def test_state_size_is_40(self):
        assert STATE_SIZE == 40

    def test_replay_capacity_is_50k(self):
        assert REPLAY_CAPACITY == 50_000

    def test_epsilon_decay_is_slower(self):
        assert EPSILON_DECAY >= 0.998

    def test_q_net_accepts_40_features(self):
        brain = BabyBrain()
        state = np.zeros(40, dtype=np.float32)
        action = brain.select_action(state)
        assert 0 <= action < 5


class TestDoubleDQNLearning:
    def test_brain_trains_without_error(self):
        brain = BabyBrain()
        for _ in range(70):
            s = np.random.rand(STATE_SIZE).astype(np.float32)
            ns = np.random.rand(STATE_SIZE).astype(np.float32)
            brain.remember(s, 0, 1.0, ns, False)
        brain.train()
        assert brain.last_loss >= 0.0

    def test_weights_change_after_training(self):
        brain = BabyBrain()
        before = [p.clone() for p in brain.q_net.parameters()]
        for _ in range(70):
            s = np.random.rand(STATE_SIZE).astype(np.float32)
            ns = np.random.rand(STATE_SIZE).astype(np.float32)
            brain.remember(s, 0, 1.0, ns, False)
        brain.train()
        after = list(brain.q_net.parameters())
        changed = any(not torch.equal(b, a) for b, a in zip(before, after))
        assert changed

    def test_train_steps_increments(self):
        brain = BabyBrain()
        for _ in range(70):
            s = np.random.rand(STATE_SIZE).astype(np.float32)
            ns = np.random.rand(STATE_SIZE).astype(np.float32)
            brain.remember(s, 0, 1.0, ns, False)
        brain.train()
        assert brain.train_steps == 1

    def test_epsilon_decays_after_training(self):
        brain = BabyBrain()
        brain.epsilon = 0.5
        for _ in range(70):
            s = np.random.rand(STATE_SIZE).astype(np.float32)
            ns = np.random.rand(STATE_SIZE).astype(np.float32)
            brain.remember(s, 0, 1.0, ns, False)
        brain.train()
        assert brain.epsilon < 0.5

    def test_no_train_if_buffer_too_small(self):
        brain = BabyBrain()
        brain.train()
        assert brain.train_steps == 0
        assert brain.last_loss == 0.0
