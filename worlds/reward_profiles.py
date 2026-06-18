"""
Perfiles de recompensa por tipo de mundo.
Cada mundo ajusta el valor de los eventos segun su naturaleza.
"""

REWARD_PROFILES: dict[str, dict[str, float]] = {
    "home": {
        "safe_step": 0.02,  # cada paso en casa
        "return_home_base": 10.0,  # regreso simple
        "return_after_explore": 20.0,  # regreso tras haber explorado con exito
    },
    "food": {
        "eat_food": 5.0,
        "energy_restore": 2.0,
        "return_home_bonus": 15.0,
        "step_penalty": -0.02,
    },
    "danger": {
        "survive_step": 0.3,
        "survive_danger_zone": 8.0,
        "danger_penalty": -5.0,
        "return_home_bonus": 20.0,
        "step_penalty": -0.03,
    },
    "curiosity": {
        "discover_unknown": 6.0,
        "confirm_concept": 8.0,
        "return_home_bonus": 15.0,
        "step_penalty": -0.02,
    },
    "challenge": {
        "solve_step": 0.5,
        "reach_goal": 20.0,
        "return_home_bonus": 25.0,
        "step_penalty": -0.05,
    },
}

# Penalizacion por terminar episodio fuera de casa
EPISODE_END_OUTSIDE_HOME = -10.0

# Bonus adicional al regresar con concepto nuevo descubierto
RETURN_WITH_NEW_CONCEPT = 5.0
