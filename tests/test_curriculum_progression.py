"""Tests 0.4.3: curriculum con level_completed y anti-estancamiento."""

from brain.curriculum import Curriculum, STAGNATION_THRESHOLD


class TestCurriculumLevelCompleted:
    def test_level0_completes_with_one_level_completed(self):
        c = Curriculum()
        c.record_episode(reached_goal=False, wall_hits=0, level_completed=True)
        new_level = c.check_level_up()
        assert new_level == 1

    def test_level0_does_not_complete_without_level_completed(self):
        c = Curriculum()
        for _ in range(25):
            c.record_episode(reached_goal=True, wall_hits=0, level_completed=False)
        new_level = c.check_level_up()
        assert new_level is None

    def test_level1_needs_three_completions(self):
        c = Curriculum()
        # Subir a nivel 1
        c.record_episode(reached_goal=False, wall_hits=0, level_completed=True)
        c.check_level_up()
        assert c.current_level == 1

        # Solo 2 completions → no sube
        c.record_episode(reached_goal=False, wall_hits=0, level_completed=True)
        c.record_episode(reached_goal=False, wall_hits=0, level_completed=True)
        assert c.check_level_up() is None

        # 3ra completion → sube
        c.record_episode(reached_goal=False, wall_hits=0, level_completed=True)
        assert c.check_level_up() == 2

    def test_completions_reset_after_level_up(self):
        c = Curriculum()
        c.record_episode(reached_goal=False, wall_hits=0, level_completed=True)
        c.check_level_up()
        assert c._level_completions == 0

    def test_episodes_without_progress_increments(self):
        c = Curriculum()
        for _ in range(5):
            c.record_episode(reached_goal=False, wall_hits=0, level_completed=False)
        assert c.episodes_without_progress == 5

    def test_level_completed_resets_without_progress_counter(self):
        c = Curriculum()
        for _ in range(10):
            c.record_episode(reached_goal=False, wall_hits=0)
        assert c.episodes_without_progress == 10
        c.record_episode(reached_goal=False, wall_hits=0, level_completed=True)
        assert c.episodes_without_progress == 0

    def test_stagnation_activates_after_threshold(self):
        c = Curriculum()
        for _ in range(STAGNATION_THRESHOLD):
            c.record_episode(reached_goal=False, wall_hits=0, level_completed=False)
        assert c.stagnation_active is True

    def test_stagnation_deactivates_on_level_completed(self):
        c = Curriculum()
        for _ in range(STAGNATION_THRESHOLD):
            c.record_episode(reached_goal=False, wall_hits=0, level_completed=False)
        assert c.stagnation_active is True
        c.record_episode(reached_goal=False, wall_hits=0, level_completed=True)
        assert c.stagnation_active is False

    def test_get_stats_includes_curriculum_dict(self):
        c = Curriculum()
        stats = c.get_stats()
        assert "curriculum" in stats
        assert "current_level" in stats["curriculum"]
        assert "required" in stats["curriculum"]
        assert "completed_so_far" in stats["curriculum"]

    def test_reached_goal_alone_does_not_reset_progress_counter(self):
        # 0.4.3: solo level_completed resetea el contador de progreso
        c = Curriculum()
        for _ in range(STAGNATION_THRESHOLD - 1):
            c.record_episode(reached_goal=False, wall_hits=0, level_completed=False)
        c.record_episode(reached_goal=True, wall_hits=0, level_completed=False)
        assert c.episodes_without_progress == STAGNATION_THRESHOLD
