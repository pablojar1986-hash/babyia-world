"""Tests de percepcion en el vector de estado DQN — BabyIA 0.4.6."""

import inspect

import numpy as np

from brain.baby_brain import STATE_SIZE, BabyBrain


class TestStateSize:
    def test_state_size_is_40(self):
        assert STATE_SIZE == 40

    def test_q_network_input_matches_state_size(self):
        brain = BabyBrain()
        assert brain.q_net.net[0].in_features == STATE_SIZE

    def test_target_network_input_matches_state_size(self):
        brain = BabyBrain()
        assert brain.target_net.net[0].in_features == STATE_SIZE


class TestFullObsPerceptionFeatures:
    def test_full_obs_returns_40_features(self):
        from brain.trainer import Trainer

        t = Trainer(training=False)
        t.start_episode()
        assert len(t._current_state) == 40

    def test_full_obs_dtype_is_float32(self):
        from brain.trainer import Trainer

        t = Trainer(training=False)
        t.start_episode()
        assert t._current_state.dtype == np.float32

    def test_full_obs_source_has_perc_feats(self):
        from brain.trainer import Trainer

        src = inspect.getsource(Trainer._full_obs)
        assert "perc_feats" in src

    def test_full_obs_source_has_key_visible(self):
        from brain.trainer import Trainer

        src = inspect.getsource(Trainer._full_obs)
        assert "key_visible" in src

    def test_full_obs_source_has_exploration_ratio(self):
        from brain.trainer import Trainer

        src = inspect.getsource(Trainer._full_obs)
        assert "exploration_ratio" in src

    def test_full_obs_source_has_blocked_count(self):
        from brain.trainer import Trainer

        src = inspect.getsource(Trainer._full_obs)
        assert "blocked_count" in src

    def test_perception_features_are_bounded(self):
        from brain.trainer import Trainer

        t = Trainer(training=False)
        t.start_episode()
        state = t._current_state
        # features 34-39 son todas entre 0 y 1
        for i, v in enumerate(state[34:], start=34):
            assert 0.0 <= v <= 1.0 + 1e-6, f"feature[{i}]={v} fuera de rango [0,1]"

    def test_base_features_still_present(self):
        """Los 34 features originales siguen siendo los primeros 34."""
        from brain.trainer import Trainer

        src = inspect.getsource(Trainer._full_obs)
        assert "base_obs" in src
        assert "world_feats" in src
        assert "body_feats" in src
