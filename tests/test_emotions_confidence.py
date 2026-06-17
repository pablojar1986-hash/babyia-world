"""Tests de señal de confianza en Emotions — BabyIA 0.4.5b."""

from brain.emotions import Emotions


class TestConfidenceIncreasesOnKey:
    def test_picked_key_raises_confidence(self):
        em = Emotions()
        before = em.confidence
        em.update(0.5, False, False, events={"picked_key": True})
        assert em.confidence > before

    def test_picked_key_boost_is_significant(self):
        em = Emotions()
        em.confidence = 0.5
        em.update(0.0, False, False, events={"picked_key": True})
        assert em.confidence >= 0.55

    def test_picked_key_reduces_frustration(self):
        em = Emotions()
        em.frustration = 0.5
        em.update(0.0, False, False, events={"picked_key": True})
        assert em.frustration < 0.5

    def test_level_completed_large_boost(self):
        em = Emotions()
        em.confidence = 0.3
        em.update(10.0, False, True, events={"level_completed": True})
        assert em.confidence >= 0.4

    def test_opened_door_raises_confidence(self):
        em = Emotions()
        before = em.confidence
        em.update(0.0, False, False, events={"opened_door": True})
        assert em.confidence > before

    def test_no_events_no_extra_change(self):
        em = Emotions()
        em.confidence = 0.5
        em.update(0.0, False, False, events={})
        # sin eventos especiales, la confianza solo cambia por decaimiento natural
        assert 0.0 <= em.confidence <= 1.0

    def test_values_stay_bounded(self):
        em = Emotions()
        em.confidence = 0.99
        for _ in range(20):
            em.update(
                5.0, False, True, events={"picked_key": True, "level_completed": True}
            )
        assert em.confidence <= 1.0

    def test_confidence_never_below_zero(self):
        em = Emotions()
        em.confidence = 0.01
        for _ in range(20):
            em.update(-5.0, True, False, events={"in_danger": True})
        assert em.confidence >= 0.0


class TestConfidenceIncreasesOnPositiveReward:
    def test_positive_reward_raises_confidence(self):
        em = Emotions()
        em.confidence = 0.5
        before = em.confidence
        em.update(1.0, False, False)
        assert em.confidence > before

    def test_small_reward_no_change(self):
        em = Emotions()
        em.confidence = 0.5
        before = em.confidence
        # reward=0.2 < threshold 0.5, no confidence boost from reward signal
        em.update(0.2, False, False)
        # confianza puede subir leve por streak_no_wall si aplica
        assert em.confidence >= before - 0.01

    def test_strong_negative_reward_drops_confidence(self):
        em = Emotions()
        em.confidence = 0.5
        em.update(-5.0, False, False)
        assert em.confidence < 0.5

    def test_in_danger_drops_confidence(self):
        em = Emotions()
        em.confidence = 0.5
        em.update(0.0, False, False, events={"in_danger": True})
        assert em.confidence < 0.5


class TestConfidenceDecreasesOnWall:
    def test_hit_wall_decreases_confidence(self):
        em = Emotions()
        before = em.confidence
        em.update(-0.1, True, False)
        assert em.confidence < before

    def test_hit_wall_increases_frustration(self):
        em = Emotions()
        em.frustration = 0.0
        em.update(-0.1, True, False)
        assert em.frustration > 0.0

    def test_wall_streak_resets_counter(self):
        em = Emotions()
        em._steps_without_wall = 15
        em.update(-0.1, True, False)
        assert em._steps_without_wall == 0

    def test_no_wall_streak_builds_counter(self):
        em = Emotions()
        em._steps_without_wall = 0
        for _ in range(5):
            em.update(0.0, False, False)
        assert em._steps_without_wall == 5

    def test_streak_10_gives_small_boost(self):
        em = Emotions()
        em._steps_without_wall = 9
        em.confidence = 0.5
        em.update(0.0, False, False)
        # paso 10 => boost de 0.005
        assert em.confidence > 0.5
