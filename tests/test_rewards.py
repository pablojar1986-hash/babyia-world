from world.rewards import (
    REWARD_GOAL,
    REWARD_STEP,
    REWARD_WALL,
    REWARD_NEW_CELL,
    REPEAT_WINDOW,
    calculate_reward,
)


def test_base_step_cost():
    r = calculate_reward(False, False, False, [])
    assert r == REWARD_STEP


def test_goal_reward():
    r = calculate_reward(False, True, False, [])
    assert r == round(REWARD_GOAL + REWARD_STEP, 4)


def test_wall_penalty():
    r = calculate_reward(True, False, False, [])
    assert r == round(REWARD_WALL + REWARD_STEP, 4)


def test_new_cell_bonus():
    r = calculate_reward(False, False, True, [])
    assert r == round(REWARD_NEW_CELL + REWARD_STEP, 4)


def test_repeat_action_penalty():
    history = [0] * REPEAT_WINDOW  # misma acción repetida
    r = calculate_reward(False, False, False, history)
    assert r < REWARD_STEP  # penalización adicional


def test_no_repeat_penalty_for_wait():
    history = [4] * REPEAT_WINDOW  # WAIT repetido no penaliza
    r = calculate_reward(False, False, False, history)
    assert r == REWARD_STEP


def test_goal_plus_new_cell():
    r = calculate_reward(False, True, True, [])
    assert r == round(REWARD_GOAL + REWARD_NEW_CELL + REWARD_STEP, 4)
