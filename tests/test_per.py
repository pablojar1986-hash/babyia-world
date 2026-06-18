"""Tests de Prioritized Experience Replay — BabyIA 0.4.6."""

import numpy as np

from brain.baby_brain import (
    STATE_SIZE,
    BabyBrain,
    _PER_ALPHA,
    _PER_EPSILON,
    _PrioritizedReplayBuffer,
    _SumTree,
)


class TestSumTree:
    def test_add_single_entry(self):
        tree = _SumTree(10)
        tree.add(1.0, "x")
        assert len(tree) == 1
        assert tree.total == 1.0

    def test_add_multiple_entries(self):
        tree = _SumTree(10)
        tree.add(1.0, "a")
        tree.add(3.0, "b")
        assert len(tree) == 2
        assert abs(tree.total - 4.0) < 1e-6

    def test_get_returns_valid_data(self):
        tree = _SumTree(10)
        tree.add(1.0, "x")
        idx, priority, data = tree.get(0.5)
        assert data == "x"
        assert priority == 1.0

    def test_update_changes_total(self):
        tree = _SumTree(10)
        tree.add(1.0, "a")
        idx = tree.capacity - 1
        tree.update(idx, 5.0)
        assert abs(tree.total - 5.0) < 1e-6

    def test_capacity_wraps_old_entries(self):
        tree = _SumTree(3)
        for i in range(5):
            tree.add(1.0, i)
        assert len(tree) == 3

    def test_get_high_s_returns_high_priority_leaf(self):
        tree = _SumTree(4)
        tree.add(0.01, "low")
        tree.add(10.0, "high")
        _, _, data = tree.get(tree.total * 0.99)
        assert data == "high"


class TestPERBuffer:
    def test_add_and_len(self):
        buf = _PrioritizedReplayBuffer(50)
        for i in range(10):
            buf.add((i,))
        assert len(buf) == 10

    def test_sample_returns_batch_of_correct_size(self):
        buf = _PrioritizedReplayBuffer(100)
        for i in range(70):
            buf.add((np.zeros(3), i, 0.0, np.zeros(3), False))
        batch, indices, weights = buf.sample(64)
        assert len(batch) == 64
        assert len(indices) == 64
        assert len(weights) == 64

    def test_weights_in_valid_range(self):
        buf = _PrioritizedReplayBuffer(100)
        for i in range(70):
            buf.add((np.zeros(3), i, 0.0, np.zeros(3), False))
        _, _, weights = buf.sample(64)
        assert np.all(weights >= 0.0)
        assert np.all(weights <= 1.0 + 1e-6)

    def test_update_priorities_does_not_crash(self):
        buf = _PrioritizedReplayBuffer(50)
        for i in range(50):
            buf.add((i,))
        batch, indices, _ = buf.sample(10)
        td_errors = np.random.rand(10)
        buf.update_priorities(indices, td_errors)

    def test_update_priorities_changes_max_priority(self):
        buf = _PrioritizedReplayBuffer(50)
        buf.add((0,))
        buf.add((1,))
        _, indices, _ = buf.sample(1)
        old_max = buf._max_priority
        buf.update_priorities(indices, [999.0])
        assert buf._max_priority > old_max

    def test_high_priority_sampled_more(self):
        buf = _PrioritizedReplayBuffer(100)
        buf.add(("low",))
        buf.add(("high",))
        # Forzar prioridades muy distintas directamente en el arbol
        buf._tree.update(buf._tree.capacity - 1, 0.001)  # entrada 0: baja
        buf._tree.update(buf._tree.capacity, 100.0)  # entrada 1: alta
        counts = {"low": 0, "high": 0}
        for _ in range(300):
            batch, _, _ = buf.sample(1)
            label = batch[0][0]
            counts[label] += 1
        assert counts["high"] > counts["low"]

    def test_beta_anneals_toward_one(self):
        buf = _PrioritizedReplayBuffer(100)
        for i in range(70):
            buf.add((i,))
        beta_before = buf._beta
        for _ in range(100):
            buf.sample(64)
        assert buf._beta > beta_before
        assert buf._beta <= 1.0


class TestBrainPER:
    def test_brain_buffer_is_per(self):
        brain = BabyBrain()
        assert isinstance(brain.buffer, _PrioritizedReplayBuffer)

    def test_per_alpha_and_epsilon_constants(self):
        assert 0 < _PER_ALPHA <= 1.0
        assert _PER_EPSILON > 0

    def test_brain_trains_with_per_no_error(self):
        brain = BabyBrain()
        for _ in range(70):
            s = np.random.rand(STATE_SIZE).astype(np.float32)
            ns = np.random.rand(STATE_SIZE).astype(np.float32)
            brain.remember(s, 0, 1.0, ns, False)
        brain.train()
        assert brain.train_steps == 1

    def test_priorities_updated_after_train(self):
        brain = BabyBrain()
        for _ in range(70):
            s = np.random.rand(STATE_SIZE).astype(np.float32)
            ns = np.random.rand(STATE_SIZE).astype(np.float32)
            brain.remember(s, 0, 1.0, ns, False)
        brain.train()
        # max_priority nunca debe quedar en 0
        assert brain.buffer._max_priority > 0
